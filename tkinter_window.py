from tkinter import font
import tkinter
import http.client
import smtplib
from email.mime.text import MIMEText

def extract_service_area_data(str_xml):
    from xml.etree import ElementTree
    tree = ElementTree.fromstring(str_xml)
    list_elements = tree.getiterator("list")  # 엘리먼트 리스트 추출
    table = {}
    i = 0
    for list_element in list_elements:
        # route_name = list_element.find("routeName")  # 도로 검색.
        service_area_name = list_element.find("serviceAreaName")  # 휴게소 이름 검색
        oil_company = list_element.find("oilCompany")  # 업체 검색
        diesel_price = list_element.find("diselPrice")  # 경유 기름값, 원본 데이터셋이 disel 로 오타가 나있음
        gasoline_price = list_element.find("gasolinePrice")  # 휘발유 기름값
        lpg_price = list_element.find("lpgPrice")  # LPG(액화 석유 가스) 기름값
        # if len(route_name.text) > 0:  # 제대로 된 도로 이름이 들어간 경우에만 찾아서 집어넣자.
        table[i] = {"serviceAreaName": service_area_name.text,
                    "oilCompany": oil_company.text,
                    "Diesel": diesel_price.text,
                    "Gasoline": gasoline_price.text,
                    "LPG": lpg_price.text}
        i += 1

    return table


class FrameWindow:
    def __init__(self):
        self.window = tkinter.Tk()
        self.width, self.height = 800, 600
        self.title = "기름값 일기토"
        self.labelFont = font.Font(self.window, size=15, weight='bold', family='Consolas')

        # 노선 목록 생성
        self.routeListScrollbar = tkinter.Scrollbar(self.window)
        self.routeListBox = tkinter.Listbox(self.window, font=self.labelFont, activestyle='none', width=37, height=3,
                                            borderwidth=10, relief='ridge', yscrollcommand=self.routeListScrollbar.set)

        # 휴게소 검색 버튼 생성
        self.routeSearchButton = tkinter.Button(self.window, font=self.labelFont,
                                                text="선택한 도로로\n휴게소를\n검색합니다.",
                                                command=self.search_service_area)
        self.email_button = tkinter.Button(self.window,font=(self.labelFont,13),text="전송",command=self.mail_send)
        self.email_button.pack()
        self.email_button.place(x=530,y=380)
        # 휴게소 목록 생성
        self.serviceListScrollbar = tkinter.Scrollbar(self.window)
        self.serviceListScrollbar2 = tkinter.Scrollbar(self.window)
        self.serviceAreaListbox = \
            tkinter.Listbox(self.window, font=self.labelFont, activestyle='none', width=10, height=3, borderwidth=5,
                            relief='flat', yscrollcommand=self.serviceListScrollbar.set)
        self.serviceAreaListbox2 = \
            tkinter.Listbox(self.window, font=self.labelFont, activestyle='none', width=10, height=3, borderwidth=5,
                            relief='flat', yscrollcommand=self.serviceListScrollbar2.set)

        # 선택한 휴게소 정보 보기 버튼 생성
        self.serviceAreaInfoButton = tkinter.Button(self.window, font=self.labelFont, text="선택한 휴게소\n정보 열람",
                                                    command=self.render_service_area_info)
        self.serviceAreaInfoButton2 = tkinter.Button(self.window, font=self.labelFont, text="선택한 휴게소\n정보 열람",
                                                    command=self.render_service_area_info2)
        # 보낼 이메일 텍스트 적기


        # 휴게소 정보 텍스트 칸 생성
        self.gas_station_text = tkinter.Text(self.window, width=15, height=1, borderwidth=3, relief='solid')
        self.oil_company_text = tkinter.Text(self.window, width=10, height=1, borderwidth=3, relief='groove')
        self.diesel_text = tkinter.Text(self.window, width=10, height=1, borderwidth=3, relief='solid')
        self.gasoline_text = tkinter.Text(self.window, width=10, height=1, borderwidth=3, relief='solid')
        self.lpg_text = tkinter.Text(self.window, width=10, height=1, borderwidth=3, relief='solid')
        self.gas_station_text2 = tkinter.Text(self.window, width=15, height=1, borderwidth=3, relief='solid')
        self.oil_company_text2 = tkinter.Text(self.window, width=10, height=1, borderwidth=3, relief='groove')
        self.diesel_text2 = tkinter.Text(self.window, width=10, height=1, borderwidth=3, relief='solid')
        self.gasoline_text2 = tkinter.Text(self.window, width=10, height=1, borderwidth=3, relief='solid')
        self.lpg_text2 = tkinter.Text(self.window, width=10, height=1, borderwidth=3, relief='solid')
        self.email_box = tkinter.Entry(self.window, font=self.labelFont, width=25,
                                       borderwidth=3, relief='solid')
        self.service_area_data = {}  # 휴게소의 업체, 기름값 정보 등이 저장된 데이터 딕셔너리 초기화
        self.service_area_data2 = {}

        self.create_tk()    # 멤버 변수 초기화 이외의 tk 윈도우 프레임 조립

        self.window.mainloop()  # 초기화 이후 메인 루프 시행

    def create_tk(self):
        self.window.wm_title(self.title)
        self.window.geometry(str(self.width)+'x'+str(self.height))
        self.create_route_listbox()
        self.create_service_area_listbox()
        self.create_service_area_listbox2()
        self.create_static_text_label()
        self.initinputlabel()

    def create_route_listbox(self):
        self.routeListScrollbar.place(x=self.width - 170, y=self.height - 100, height=90)
        self.routeListScrollbar.config(command=self.routeListBox.yview)
        self.routeListBox.place(x=self.width // 4, y=self.height - 100)

        self.routeSearchButton.pack()
        self.routeSearchButton.place(x=self.width - 150, y=self.height - 95)

        # 고속도로 목록 초기화 - 하드코딩
        # 인덱스는 어차피 0, 1, 2... 로 들어가지만, 루트코드를 기억하기 편하기 위해 이렇게 미리 기입해둔다.
        self.routeListBox.insert(1, "경부고속도로")
        self.routeListBox.insert(10, "남해고속도로")
        self.routeListBox.insert(12, "무안광주고속도로, 광주대구고속도로")
        self.routeListBox.insert(15, "서해안고속도로")
        # self.routeListBox.insert(16, "울산고속도로")  # 휴게소가 없어요.
        # self.routeListBox.insert(17, "익산평택고속도로, 평택파주고속도로")  # 휴게소가 없어요.
        self.routeListBox.insert(20, "새만금포항고속도로")
        self.routeListBox.insert(25, "호남고속도로, 논산천안고속도로")
        self.routeListBox.insert(27, "순천완주고속도로")
        # self.routeListBox.insert(29, "세종포천고속도로")  # 휴게소가 없어요.
        self.routeListBox.insert(30, "당진영덕고속도로")
        #  self.routeListBox.insert(32, "아산청주고속도로")  # 휴게소가 없어요.
        self.routeListBox.insert(35, "통영대전고속도로, 중부고속도로")
        # self.routeListBox.insert(37, "제2중부고속도로")  # 휴게소가 없어요.
        self.routeListBox.insert(40, "평택제천고속도로")
        self.routeListBox.insert(45, "중부내륙고속도로")
        self.routeListBox.insert(50, "영동고속도로")
        # self.routeListBox.insert(52, "광주원주고속도로")  # 휴게소가 없어요.
        self.routeListBox.insert(55, "중앙고속도로")
        self.routeListBox.insert(60, "서울양양고속도로")
        self.routeListBox.insert(65, "동해고속도로")
        self.routeListBox.insert(100, "서울외곽순환고속도로")
        # self.routeListBox.insert(102, "남해고속도로 제1지선")  # 휴게소가 없어요.
        self.routeListBox.insert(104, "남해고속도로 제2지선")
        # self.routeListBox.insert(105, "남해고속도로 제3지선(부산항신항고속도로)")  # 휴게소가 없어요.
        # self.routeListBox.insert(110, "제2경인고속도로")  # 휴게소가 없어요.
        # self.routeListBox.insert(120, "경인고속도로")  # 휴게소가 없어요.
        # self.routeListBox.insert(130, "인천국제공항고속도로")  # 휴게소가 없어요.
        self.routeListBox.insert(151, "서천공주고속도로")
        # self.routeListBox.insert(153, "평택시흥고속도로")  # 휴게소가 없어요.
        # self.routeListBox.insert(171, "오산화성고속도로, 용인서울고속도로")  # 휴게소가 없어요.
        # self.routeListBox.insert(204, "새만금포항고속도로지선")  # 휴게소가 없어요.
        self.routeListBox.insert(251, "호남고속도로")
        # self.routeListBox.insert(253, "고창담양고속도로")  # 휴게소가 없어요.
        # self.routeListBox.insert(300, "대전남부순환고속도로")  # 휴게소가 없어요.
        # self.routeListBox.insert(301, "상주영천고속도로")  # 휴게소가 없어요.
        # self.routeListBox.insert(400, "수도권 제2순환고속도로")  # 휴게소가 없어요.
        self.routeListBox.insert(451, "중부내륙고속도로지선")
        # self.routeListBox.insert(551, "중앙고속도로지선")  # 휴게소가 없어요.
        self.routeListBox.insert(600, "부산외곽순환고속도로")

    def create_static_text_label(self):
        self.gas_station_text.place(x=50, y=self.height - 450)
        self.gas_station_text.configure(state='disabled')
        tkinter.Label(self.window, font=self.labelFont, text="업체 : ").place(x=10, y=self.height - 500)
        self.oil_company_text.place(x=100, y=self.height - 500)
        self.oil_company_text.configure(state='disabled')
        tkinter.Label(self.window, font=self.labelFont, text="경유(디젤) 가격").place(x=10, y=self.height - 400)
        self.diesel_text.place(x=10, y=self.height - 370)
        self.diesel_text.configure(state='disabled')
        tkinter.Label(self.window, font=self.labelFont, text="휘발유(가솔린) 가격").place(x=10, y=self.height - 300)
        self.gasoline_text.place(x=10, y=self.height - 270)
        self.gasoline_text.configure(state='disabled')
        tkinter.Label(self.window, font=self.labelFont, text="LPG 가격").place(x=10, y=self.height - 200)
        self.lpg_text.place(x=10, y=self.height - 170)
        self.lpg_text.configure(state='disabled')

        #왼쪽
        self.gas_station_text2.place(x=650, y=self.height - 450)
        self.gas_station_text2.configure(state='disabled')
        tkinter.Label(self.window, font=self.labelFont, text="업체 : ").place(x=640, y=self.height - 500)
        self.oil_company_text2.place(x=720, y=self.height - 500)
        self.oil_company_text2.configure(state='disabled')
        tkinter.Label(self.window, font=self.labelFont,text="경유(디젤) 가격").place(x=640, y=self.height - 400)
        self.diesel_text2.place(x=720, y=self.height - 370)
        self.diesel_text2.configure(state='disabled')
        tkinter.Label(self.window, font=self.labelFont, text="휘발유(가솔린) 가격").place(x=600, y=self.height - 300)
        self.gasoline_text2.place(x=720, y=self.height - 270)
        self.gasoline_text2.configure(state='disabled')
        tkinter.Label(self.window, font=self.labelFont, text="LPG 가격").place(x=710, y=self.height - 200)
        self.lpg_text2.place(x=720, y=self.height - 170)
        self.lpg_text2.configure(state='disabled')


        tkinter.Label(self.window, font=self.labelFont, text="휴게소를 검색할").place(x=5, y=self.height - 75)
        tkinter.Label(self.window, font=self.labelFont, text="도로를 클릭하세요.").place(x=5, y=self.height - 50)
    def initinputlabel(self):
        tkinter.Label(self.window, font=self.labelFont, text="전송할 이메일 입력").place(x=320, y=self.height - 250)
        self.email_box.pack()
        self.email_box.place(x=250, y=self.height - 220)
        #self.email_box.configure(state='disabled')
    def create_service_area_listbox(self):
        self.serviceListScrollbar.pack()
        self.serviceListScrollbar.place(x=135, y=0, height=90)

        self.serviceAreaListbox.pack()
        self.serviceAreaListbox.place(x=10, y=0)
        self.serviceListScrollbar.config(command=self.serviceAreaListbox.yview)

        self.serviceAreaInfoButton.pack()
        self.serviceAreaInfoButton.place(x=155, y=1)
    def create_service_area_listbox2(self):
        self.serviceListScrollbar2.pack()
        self.serviceListScrollbar2.place(x=780, y=0, height=90)

        self.serviceAreaListbox2.pack()
        self.serviceAreaListbox2.place(x=660, y=0)
        self.serviceListScrollbar2.config(command=self.serviceAreaListbox2.yview)

        self.serviceAreaInfoButton2.pack()
        self.serviceAreaInfoButton2.place(x=510, y=1)
    def search_service_area(self):
        if self.routeListBox.curselection() is not ():
            search_index = self.routeListBox.curselection()[0]
            # 장대한 하드코딩의 시작. 이게 다 python 에 switch 문이 없는 탓이다.
            '''
            # 휴게소가 없는 고속도로를 제외하지 않았을 때.
            if searchIndex is 0:
                routeCode = 1
            elif searchIndex is 1:
                routeCode = 10
            elif searchIndex is 2:
                routeCode = 12
            elif searchIndex is 3:
                routeCode = 15
            elif searchIndex is 4:
                routeCode = 16
            elif searchIndex is 5:
                routeCode = 17
            elif searchIndex is 6:
                routeCode = 20
            elif searchIndex is 7:
                routeCode = 25
            elif searchIndex is 8:
                routeCode = 27
            elif searchIndex is 9:
                routeCode = 29
            elif searchIndex is 10:
                routeCode = 30
            elif searchIndex is 11:
                routeCode = 32
            elif searchIndex is 12:
                routeCode = 35
            elif searchIndex is 13:
                routeCode = 37
            elif searchIndex is 14:
                routeCode = 40
            elif searchIndex is 15:
                routeCode = 45
            elif searchIndex is 16:
                routeCode = 50
            elif searchIndex is 17:
                routeCode = 52
            elif searchIndex is 18:
                routeCode = 55
            elif searchIndex is 19:
                routeCode = 60
            elif searchIndex is 20:
                routeCode = 65
            elif searchIndex is 21:
                routeCode = 100
            elif searchIndex is 22:
                routeCode = 102
            elif searchIndex is 23:
                routeCode = 104
            elif searchIndex is 24:
                routeCode = 105
            elif searchIndex is 25:
                routeCode = 110
            elif searchIndex is 26:
                routeCode = 120
            elif searchIndex is 27:
                routeCode = 130
            elif searchIndex is 28:
                routeCode = 151
            elif searchIndex is 29:
                routeCode = 153
            elif searchIndex is 30:
                routeCode = 171
            elif searchIndex is 31:
                routeCode = 204
            elif searchIndex is 32:
                routeCode = 251
            elif searchIndex is 33:
                routeCode = 253
            elif searchIndex is 34:
                routeCode = 300
            elif searchIndex is 35:
                routeCode = 301
            elif searchIndex is 36:
                routeCode = 400
            elif searchIndex is 37:
                routeCode = 451
            elif searchIndex is 38:
                routeCode = 551
            elif searchIndex is 39:
                routeCode = 600
            else:
                routeCode = 0
            '''
            if search_index is 0:
                route_code = 1
            elif search_index is 1:
                route_code = 10
            elif search_index is 2:
                route_code = 12
            elif search_index is 3:
                route_code = 15
            elif search_index is 4:
                route_code = 20
            elif search_index is 5:
                route_code = 25
            elif search_index is 6:
                route_code = 27
            elif search_index is 7:
                route_code = 30
            elif search_index is 8:
                route_code = 35
            elif search_index is 9:
                route_code = 40
            elif search_index is 10:
                route_code = 45
            elif search_index is 11:
                route_code = 50
            elif search_index is 12:
                route_code = 55
            elif search_index is 13:
                route_code = 60
            elif search_index is 14:
                route_code = 65
            elif search_index is 15:
                route_code = 100
            elif search_index is 16:
                route_code = 104
            elif search_index is 17:
                route_code = 151
            elif search_index is 18:
                route_code = 251
            elif search_index is 19:
                route_code = 451
            elif search_index is 20:
                route_code = 600
            else:
                route_code = 0
            self.data_request_from_route_code(route_code)
        else:
            print("이상한 짓 하지 말고 도로부터 고르십시오.")

    def data_request_from_route_code(self, route_code):
        route_code_string = str(route_code)
        if route_code == 0:
            print("뭔가 하드코딩하다가 잘못된 것 같은데, 다시 확인해 보십시오.")
            return 0
        elif route_code < 10:
            route_code_string = "00"+str(route_code)
        elif route_code < 100:
            route_code_string = '0'+str(route_code)
        elif route_code >= 1000:
            print(route_code, "번 같은 고속도로 번호는 대한민국에 존재하지 않습니다.")
        conn = http.client.HTTPConnection("data.ex.co.kr")
        # hangul_utf8 = urllib.parse.quote("한국산업기술대학교")
        conn.request("GET",
                     "/exopenapi/business/curStateStation?"
                     "serviceKey="
                     "RnNkEfETohNvlvmujzG2DwaWYE6X%2Foj3Z8XeB7lG%2BWMhsUj29X1atIRExX1L00Ubb4kSIUcLWrZzpy5djZ8Wuw%3D%3D&"
                     "type=xml&numOfRows=50&pageNo=1&routeCode=" + route_code_string+'0')

        req = conn.getresponse()
        # print(req.status, req.reason)
        self.service_area_data.clear()
        self.service_area_data = extract_service_area_data(req.read().decode('utf-8'))
        #self.service_area_data2.clear()
        #self.service_area_data2 = extract_service_area_data(req.read().decode('utf-8'))
        # 이전에 검색했던 휴게소 데이터 리스트를 싹 청소한다.
        self.serviceAreaListbox.delete(0, self.serviceAreaListbox.size())
        self.serviceAreaListbox2.delete(0, self.serviceAreaListbox2.size())
        for service_area_index in self.service_area_data:
            self.serviceAreaListbox.insert(service_area_index,
                                           self.service_area_data[service_area_index]["serviceAreaName"])
        for service_area_index in self.service_area_data:
            self.serviceAreaListbox2.insert(service_area_index,
                                           self.service_area_data[service_area_index]["serviceAreaName"])

    def render_service_area_info(self):
        if self.serviceAreaListbox.curselection() is not ():
            search_index = self.serviceAreaListbox.curselection()[0]
            for service_area_index in self.service_area_data:
                if service_area_index == search_index:
                    self.gas_station_text.configure(state='normal')
                    self.oil_company_text.configure(state='normal')
                    self.diesel_text.configure(state='normal')
                    self.gasoline_text.configure(state='normal')
                    self.lpg_text.configure(state='normal')
                    self.gas_station_text.delete(0.0, tkinter.END)
                    self.oil_company_text.delete(0.0, tkinter.END)
                    self.diesel_text.delete(0.0, tkinter.END)
                    self.gasoline_text.delete(0.0, tkinter.END)
                    self.lpg_text.delete(0.0, tkinter.END)

                    # print(self.service_area_data[service_area_index])

                    self.oil_company_text.insert(tkinter.INSERT,
                                                  self.service_area_data[service_area_index]["oilCompany"])
                    self.diesel_text.insert(tkinter.INSERT,
                                             self.service_area_data[service_area_index]["Diesel"])
                    self.gasoline_text.insert(tkinter.INSERT,
                                               self.service_area_data[service_area_index]["Gasoline"])
                    self.lpg_text.insert(tkinter.INSERT,
                                          self.service_area_data[service_area_index]["LPG"])
                    self.gas_station_text.insert(tkinter.INSERT,
                                                  self.service_area_data[service_area_index]["serviceAreaName"])
                    self.oil_company_text.configure(state='disabled')
                    self.diesel_text.configure(state='disabled')
                    self.gasoline_text.configure(state='disabled')
                    self.lpg_text.configure(state='disabled')
                    break
    def render_service_area_info2(self):
        if self.serviceAreaListbox2.curselection() is not ():
            search_index = self.serviceAreaListbox2.curselection()[0]
            for service_area_index in self.service_area_data:
                if service_area_index == search_index:
                    self.gas_station_text2.configure(state='normal')
                    self.oil_company_text2.configure(state='normal')
                    self.diesel_text2.configure(state='normal')
                    self.gasoline_text2.configure(state='normal')
                    self.lpg_text2.configure(state='normal')
                    self.gas_station_text2.delete(0.0, tkinter.END)
                    self.oil_company_text2.delete(0.0, tkinter.END)
                    self.diesel_text2.delete(0.0, tkinter.END)
                    self.gasoline_text2.delete(0.0, tkinter.END)
                    self.lpg_text2.delete(0.0, tkinter.END)

                    # print(self.service_area_data[service_area_index])

                    self.oil_company_text2.insert(tkinter.INSERT,
                                                 self.service_area_data[service_area_index]["oilCompany"])
                    self.diesel_text2.insert(tkinter.INSERT,
                                            self.service_area_data[service_area_index]["Diesel"])
                    self.gasoline_text2.insert(tkinter.INSERT,
                                              self.service_area_data[service_area_index]["Gasoline"])
                    self.lpg_text2.insert(tkinter.INSERT,
                                         self.service_area_data[service_area_index]["LPG"])
                    self.gas_station_text2.insert(tkinter.INSERT,
                                                 self.service_area_data[service_area_index]["serviceAreaName"])
                    self.oil_company_text2.configure(state='disabled')
                    self.diesel_text2.configure(state='disabled')
                    self.gasoline_text2.configure(state='disabled')
                    self.lpg_text2.configure(state='disabled')
                    break
    def mail_send(self):
        s = smtplib.SMTP('smtp.gmail.com',587)
        s.ehlo()
        s.starttls()
        sendAdress = 'rejal6457@gmail.com'
        password = ''
        s.login(sendAdress,password)
        receiveAdress = self.email_box.get()
        msgText = '휴게소 이름'
        msg = MIMEText(msgText)
        msg['Subject'] = '제목'
        msg['To'] = receiveAdress
        s.sendmail(sendAdress,receiveAdress,msg.as_string())
        s.quit()



tk = FrameWindow()
