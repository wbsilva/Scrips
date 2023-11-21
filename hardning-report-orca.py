# pacote instaldo pdf2 - pip install fpdf2
# https://py-pdf.github.io/fpdf2/Tutorial-pt.html

import requests
import simplejson
import boto3
import os
from fpdf import FPDF
from datetime import datetime

current_datetime = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')


url     = "https://api.orcasecurity.io/api/compliance/frameworks/iso_27001/tests"
url2    = "https://api.orcasecurity.io/api/compliance/frameworks"
url3    = "https://api.orcasecurity.io/api/compliance/frameworks/iso_27001/categories"
url4    = "https://api.orcasecurity.io/api/alerts?state.risk_level=high&state.status=open"
url5    = "https://api.orcasecurity.io/api/alerts?state.risk_level=critical&state.status=open"
url6    = "https://api.orcasecurity.io/api/compliance/frameworks/aws_foundational_security_best_practices/tests"

token = os.environ['tokenOrca']

headers = {
  'Authorization': f'Token {token}'
}

# Index Rel orca 27001
allData = []

page_index = 0
page_size = 1000
next = True

# Orca 27001
while next:

  response = requests.request("POST", url, headers=headers, data={
    'limit': page_size,
    'start_at_index': page_index
  })

  page_index = (page_index + page_size)

  arrResponse = simplejson.loads(response.text)   
  if len(arrResponse['data']['tests']) == 0:
    next = False
  else:
    allData = allData + arrResponse['data']['tests']
  
# Index Rel AWS Fundation
allDataAWS = []

page_index1 = 0
page_size1 = 1000
next1 = True

# AWS Fundation
while next1:

  response = requests.request("POST", url6, headers=headers, data={
    'limit': page_size1,
    'start_at_index': page_index1
  })

  page_index1 = (page_index1 + page_size1)

  arrResponse1 = simplejson.loads(response.text)   
  if len(arrResponse1['data']['tests']) == 0:
    next1 = False
  else:
    allDataAWS = allDataAWS + arrResponse1['data']['tests']

# Payload url2, url3, url4 e url5
payload = {}

responseUrl2 = requests.request("GET", url2, headers=headers, data=payload)
responseUrl3 = requests.request("GET", url3, headers=headers, data=payload)
responseUrl4 = requests.request("GET", url4, headers=headers, data=payload)
responseUrl5 = requests.request("GET", url5, headers=headers, data=payload)

# Create a dict report orca 27001
allData = {
  "data": {
    "total_count": len(allData),
    "tests": allData
  }
}

# Create a dict reposrt AWS fundation
allDataAWS = {
  "data": {
    "total_count": len(allDataAWS),
    "tests": allDataAWS
  }
}

if responseUrl2.status_code == 200:
  relHeaderAvg    = simplejson.loads(responseUrl2.text)  

else:
  print(f"Erro na requisição para {url2}:", responseUrl2.status_code) 

if responseUrl3.status_code == 200:
  relCategory  = simplejson.loads(responseUrl3.text)

else:
  print(f"Erro na requisição para {url3}:", responseUrl3.status_code) 

if responseUrl4.status_code == 200:
  relAlertsHigh  = simplejson.loads(responseUrl4.text)

else:
  print(f"Erro na requisição para {url4}:", responseUrl4.status_code)

if responseUrl5.status_code == 200:
  relAlertsCritical  = simplejson.loads(responseUrl5.text)

else:
  print(f"Erro na requisição para {url5}:", responseUrl5.status_code)

# Create PDF 
calssification = 'Classificação: Confidencial'

class PDF(FPDF): 

  # Page Header
  def header(self):    
    # font
    self.set_font('helvetica', 'B', 10)
    # Calculate width of title and position
    calssification_w = self.get_string_width(calssification) + 6
    doc_w = self.w
    self.set_x((doc_w - calssification_w) / 2)    
    # Thickness of frame (border)
    self.set_line_width(1)
    # Title
    self.cell(calssification_w, 10, calssification, border=1, new_x="LMARGIN", new_y="NEXT", align='C')
    # Line break
    self.ln(10)    

  # Chapter title
  def chapter_tilte(self, ch_num, ch_title):      
    #set font
    self.set_font('helvetica', 'B', 15)
    #chapter title
    chapter_title = f'{ch_num} {ch_title}'
    self.cell(0, 5, chapter_title, new_x="LMARGIN", new_y="NEXT")
    #line break
    self.ln()

  # Chapter content
  def chapter_body(self, content_function):      
    #set font
    self.set_font('helvetica', '', 10)
    # Chamar a função de conteúdo fornecida como argumento
    content_function(self)    
    # insert text
    self.multi_cell(0, 10)    

  def print_chapter(self, ch_num, ch_title, name):
    self.add_page()
    self.chapter_tilte(ch_num, ch_title)
    self.chapter_body(name)
    #line break
    self.ln(15)

  # Page footer
  def footer(self):
    # Set position of the footer
    self.set_y(-15)
    #  Set font
    self.set_font('helvetica', 'I', 8)
    # Page number
    self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

pdf = PDF('P', 'mm', 'A4')

# Set auto page break
pdf.set_auto_page_break(auto = True, margin = 15)   

#pdf.add_font("dejavu-sans", style="", fname="/opt/report/DejaVuSans.ttf")

def capa(pdf):
  pdf.set_font('helvetica', 'B', 20)
  pdf.image('/opt/report/header.png', 0, 0, 215)
  title = 'Relatório de hardening dos serviços Cloud'
  title_w = pdf.get_string_width(title)
  x = (pdf.w - title_w) / 2
  pdf.text(x, pdf.h / 2, title)  

def introducao(pdf):
  
  pdf.multi_cell(190, 10, f'Este documento tem como objetivo apresentar o resultado e a postura de segurança adotada pela infraestrutura cloud oferecida pela SoftExpert aos seus clientes.  ', new_x="LMARGIN", new_y="NEXT")
  pdf.multi_cell(190, 10, f'Seguindo as boas práticas de Segurança da informação, todas as configurações padrões dos serviços utilizados na infraestrutura cloud são revisadas pelo time de operações, garantindo que usuários e senhas padrões não sejam utilizados, bem como somente serviços e portas de rede necessários rodem nos servidores e estejam publicados para internet.', new_x="LMARGIN", new_y="NEXT")
  pdf.multi_cell(190, 10, f'Tais relatórios permitem a validação de vários controles de segurança implementados em serviços, infraestrutura e aplicação, atestando a compliance com vários requisitos de postura amplamente conhecidos no mercado.', new_x="LMARGIN", new_y="NEXT")
  pdf.multi_cell(190, 10, f'Este documento deve ser considerado estritamente confidencial, de acordo com a Política de Classificação de Informações da SoftExpert. Ao aceitar esta isenção de responsabilidade, os sujeitos de posse do Documento comprometem-se a considerá-lo estritamente confidencial e, portanto, não divulgarão e/ou darão o conhecimento do Documento a terceiros, no todo ou em parte, ou as informações nele contidos e nem a existência do conteúdo deste Documento.', new_x="LMARGIN", new_y="NEXT")

def ferrUtilizadas(pdf):

  pdf.multi_cell(190, 10, f'Utilizamos dois serviços AWS Security Hub e Sophos CloudOptix que oferecem o monitoramento e confrontamento das melhores práticas de segurança que uma infraestrutura deve seguir para ter uma postura de segurança adequada em serviços cloud.', new_x="LMARGIN", new_y="NEXT")
  
  pdf.set_font('helvetica', style="B", size=10)
  pdf.cell(0, 10, f'AWS Security Hub:', new_x="LMARGIN", new_y="NEXT")
  pdf.set_font('helvetica', size=10)
  pdf.multi_cell(190, 10, f'É um serviço de gerenciamento de postura de segurança na nuvem que realiza verificações de práticas recomendadas de segurança contínuas e automatizadas em relação aos seus recursos da AWS. O Security Hub permite que entendemos nossa postura geral de segurança por meio de uma pontuação de segurança consolidada das nossas contas da AWS. O serviço avalia automaticamente a segurança dos recursos utilizados em nossa cloud por meio do padrão AWS Foundational Security  Best Practices e outras estruturas de conformidade. Para mais detalhes: https://aws.amazon.com/security-hub/features/?nc=sn&loc=2', new_x="LMARGIN", new_y="NEXT")

  pdf.set_font('helvetica', style="B", size=10)
  pdf.cell(0, 10, f'Sophos CloudOptix:', new_x="LMARGIN", new_y="NEXT")
  pdf.set_font('helvetica', size=10)
  pdf.multi_cell(190, 10, f'É um serviço que oferece uma visão completa dos recursos na nuvem em ambientes multinuvem, monitorando custos e detectando implantações e configurações não seguras, anomalias de acesso, funções de IAM com excesso de privilégios e falhas de conformidade, desde o desenvolvimento até a segurança contínua dos serviços ativos. Para mais detalhes: https://www.sophos.com/pt-br/products/cloud-optix', new_x="LMARGIN", new_y="NEXT")

  pdf.set_font('helvetica', style="B", size=10)
  pdf.cell(0, 10, f'ORCA Security:', new_x="LMARGIN", new_y="NEXT")
  pdf.set_font('helvetica', size=10)
  pdf.multi_cell(190, 10, f'É um serviço que detecta os riscos de segurança mais críticos, em cada camada de sua propriedade na nuvem. Em minutos, o Orca detecta malware, vulnerabilidades, configurações incorretas, senhas vazadas e fracas, risco de movimento lateral, dados confidenciais e muito mais. Para mais detalhes: https://orca.security/', new_x="LMARGIN", new_y="NEXT")

def relOrcaAlerts(pdf):        
    # Inicialize uma variável para rastrear o valor anterior da subcategoria
    categoria_anterior = None
    subcategoria_anterior = None
    subsubcategiria_anterior = None
    totalAlerts = relAlertsHigh["total_items"] + relAlertsCritical["total_items"]

    pdf.set_font(style="B", size=13)
    pdf.cell(0, 10, f'Orca Security Alerts                                                                                    Total alertas:{totalAlerts}', new_x="LMARGIN", new_y="NEXT")    
    pdf.set_font('helvetica', '', 10)

    # Alerts Critical
    for alertsdata in relAlertsCritical["data"]:
      
        # Verifique se a categoria atual é diferente da anterior
        if alertsdata["category"] != categoria_anterior:
            pdf.set_font(style="B")
            pdf.cell(0, 10, f'Categoria: {alertsdata["category"]}', new_x="LMARGIN", new_y="NEXT")
            categoria_anterior = alertsdata["category"]

        if alertsdata["type_string"] != subcategoria_anterior:
        
            pdf.cell(0, 10, f'Tipo: {alertsdata["type_string"]}', new_x="LMARGIN", new_y="NEXT")
            subcategoria_anterior = alertsdata["type_string"]
    
        if alertsdata["group_type_string"] != subsubcategiria_anterior:

            pdf.cell(0, 10, f'Grupo: {alertsdata["group_type_string"]}', new_x="LMARGIN", new_y="NEXT")
            subsubcategiria_anterior = alertsdata["group_type_string"]
        pdf.set_font('helvetica', '', 9)
        pdf.multi_cell(0, 10, f'{alertsdata["state"]["orca_score"]} {alertsdata["source"]} Asset: {alertsdata["asset_name"]} Status: {alertsdata["state"]["status"]}', align='L', new_x="LMARGIN", new_y="NEXT")
        
    # Alerts High
    for alertsdata in relAlertsHigh["data"]:  

        # Verifique se a categoria atual é diferente da anterior
        if alertsdata["category"] != categoria_anterior:
            pdf.set_font(style="B")
            pdf.cell(0, 10, f'Categoria: {alertsdata["category"]}', new_x="LMARGIN", new_y="NEXT")
            categoria_anterior = alertsdata["category"]

        if alertsdata["type_string"] != subcategoria_anterior:
            pdf.set_font(style="B")
            pdf.cell(0, 10, f'Tipo: {alertsdata["type_string"]}', new_x="LMARGIN", new_y="NEXT")
            subcategoria_anterior = alertsdata["type_string"]
    
        if alertsdata["group_type_string"] != subsubcategiria_anterior:
            pdf.set_font(style="B")
            pdf.cell(0, 10, f'Grupo: {alertsdata["group_type_string"]}', new_x="LMARGIN", new_y="NEXT")
            subsubcategiria_anterior = alertsdata["group_type_string"]
        pdf.set_font('helvetica', '', 9)
        pdf.multi_cell(190, 10, f'{alertsdata["state"]["orca_score"]} {alertsdata["source"]} Asset: {alertsdata["asset_name"]} Status: {alertsdata["state"]["status"]}', align='L', border=1, new_x="LMARGIN", new_y="NEXT")
        
def relOrca27001(pdf):
    # Inicialize uma variável para rastrear o valor anterior da subcategoria
    categoria_anterior = None 
    subcategoria_anterior = None
    desired_value = "ISO 27001"
    framework_data = None  
  
    for framework in relHeaderAvg["data"]["frameworks"]:
        if framework["version_agnostic_display_name"] == desired_value:
            framework_data = framework
            break

    if framework_data:
        pdf.set_font(style="B", size=13)
        pdf.cell(0, 10, f'Orca - {framework_data["version_agnostic_display_name"]}', new_x="LMARGIN", new_y="NEXT") 
        pdf.set_font('helvetica', style="B", size=10)
        pdf.cell(0, 10, f'Account Name: {framework_data["top_accounts"][0]["759087766678"]["account_name"]}                                                                         Average Score - {framework_data["avg_score_percent"]}%', new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, f'Results: PASS: {framework_data["test_results"]["PASS"]} - FAIL: {framework_data["test_results"]["FAIL"]} - UNSCORED: {framework_data["test_results"]["UNSCORED"]}', new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, f'Categories: Total:  {framework_data["categories"]["total_count"]}', new_x="LMARGIN", new_y="NEXT")

    for body in allData["data"]["tests"]:

        if body["result"] != "UNSCORED":
            # Verifique se a categoria atual é diferente da anterior
            if body["category"] != categoria_anterior:
            
                pdf.set_font('helvetica', style="B", size=10)
                pdf.cell(0, 10, f'{body["category"]}', new_x="LMARGIN", new_y="NEXT")
                categoria_anterior = body["category"] 

            # Verifique se a subcategoria atual é diferente da anterior
            if body["subcategory"] != subcategoria_anterior:
            
                pdf.set_font('helvetica', style="B", size=10)
                pdf.cell(0, 10, f'{body["subcategory"]}', new_x="LMARGIN", new_y="NEXT")
                subcategoria_anterior = body["subcategory"]  

            pdf.set_font('helvetica', '', 9)   
            pdf.multi_cell(190, 10, f'{body["id"]} - {body["result"]} - {body["priority"]} - {body["description"]}', border=1, new_x="LMARGIN", new_y="NEXT")      

            if len(body["rule_id"]) > 0:
                url9 = "https://api.orcasecurity.io/api/compliance/frameworks/iso_27001/tests/"+body['rule_id']+"/alerts"
                responseUrl9 = requests.request("GET", url9, headers=headers, data=payload)

                if responseUrl9.status_code == 200:
                    ruleIdAlerts    = simplejson.loads(responseUrl9.text)              
                
                    for alerts in ruleIdAlerts["data"]["alerts"]:
                    
                        if len(alerts["state"]["alert_id"]) > 0:
                            url10 = "https://api.orcasecurity.io/api/alerts/"+alerts["state"]["alert_id"]+"/event_log"
                            responseUrl10 = requests.request("GET", url10, headers=headers, data=payload)

                        if responseUrl10.status_code == 200:
                            eventLog    = simplejson.loads(responseUrl10.text) 

                            for event in eventLog["event_log"]:
                                details = event["details"]
                                comment = details.get("comment", "")                  

                                if comment.strip() != "":
                                    pdf.multi_cell(190, 10, f'Justificativa:{comment}', border=1, new_x="LMARGIN", new_y="NEXT")

                                else:
                                    pass
                        else:
                            print(f"Erro na requisição para {url10}:", responseUrl10.status_code) 
                else:
                    print(f"Erro na requisição para {url9}:", responseUrl9.status_code)                 
            else:
                pdf.multi_cell(190, 10, f'sem dados no campo rule_id', border=1, new_x="LMARGIN", new_y="NEXT")

def relAwsFundation(pdf): 
  
  # Inicialize uma variável para rastrear o valor anterior da subcategoria
  categoria_anterior = None
  desired_value = "AWS Foundational Security Best Practices"
  framework_data = None  
  
  for framework in relHeaderAvg["data"]["frameworks"]:
    if framework["version_agnostic_display_name"] == desired_value:
        framework_data = framework
        break

  if framework_data:
    pdf.set_font(style="B", size=13)
    pdf.cell(0, 10, f'AWS - {framework_data["display_name"]}', new_x="LMARGIN", new_y="NEXT") 
    pdf.set_font('helvetica', style="B", size=10)  
    pdf.cell(0, 10, f'Account Name: {framework_data["top_accounts"][0]["759087766678"]["account_name"]}                                                                         Average Score - {framework_data["avg_score_percent"]}%', new_x="LMARGIN", new_y="NEXT")  
    pdf.cell(0, 10, f'Results: PASS: {framework_data["test_results"]["PASS"]} - FAIL: {framework_data["test_results"]["FAIL"]} - UNSCORED: {framework_data["test_results"]["UNSCORED"]}', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f'Categories: Total:  {framework_data["categories"]["total_count"]}', new_x="LMARGIN", new_y="NEXT")

  for body in allDataAWS["data"]["tests"]:
    if (body["result"] != "UNSCORED"):  

       # Verifique se a subcategoria atual é diferente da anterior
      if body["category"] != categoria_anterior:
        
        pdf.set_font('helvetica', style="B", size=10)
        pdf.cell(0, 10, f'{body["category"]}', new_x="LMARGIN", new_y="NEXT")
        categoria_anterior = body["category"]
  
      pdf.set_font('helvetica', '', 9)   
      pdf.multi_cell(190, 10, f'{body["id"]} - {body["result"]} - {body["priority"]} - {body["description"]}', border=1, new_x="LMARGIN", new_y="NEXT")

      if len(body["rule_id"]) > 0:
        url7 = "https://api.orcasecurity.io/api/compliance/frameworks/aws_foundational_security_best_practices/tests/"+body['rule_id']+"/alerts"
        responseUrl7 = requests.request("GET", url7, headers=headers, data=payload)

        if responseUrl7.status_code == 200:
          ruleIdAlerts    = simplejson.loads(responseUrl7.text)              
          
          for alerts in ruleIdAlerts["data"]["alerts"]:
            
            if len(alerts["state"]["alert_id"]) > 0:
              url8 = "https://api.orcasecurity.io/api/alerts/"+alerts["state"]["alert_id"]+"/event_log"
              responseUrl8 = requests.request("GET", url8, headers=headers, data=payload)

              if responseUrl8.status_code == 200:
                eventLog    = simplejson.loads(responseUrl8.text) 

                for event in eventLog["event_log"]:
                  details = event["details"]
                  comment = details.get("comment", "")                  

                  if comment.strip() != "":
                    pdf.multi_cell(190, 10, f'Justificativa:{comment}', border=1, new_x="LMARGIN", new_y="NEXT")

                  else:
                    pass

              else:
                print(f"Erro na requisição para {url8}:", responseUrl8.status_code) 

        else:
          print(f"Erro na requisição para {url7}:", responseUrl7.status_code)    
               
      else:
        pdf.multi_cell(190, 10, f'sem dados no campo rule_id', border=1, new_x="LMARGIN", new_y="NEXT") 
  
def parecerFinal(pdf):   
  pdf.multi_cell(190, 10, f'Conforme evidências apresentadas, a SoftExpert possui controles para garantir que o hardening seja aplicado em todos os serviços e recursos utilizados na operação cloud.', new_x="LMARGIN", new_y="NEXT")
  pdf.multi_cell(190, 10, f'Todos os itens que possam gerar algum risco para os ambientes são mitigados e constantemente validados e em casos de alguma inconsistência, são gerados alertas e incidentes para o time de operações cloud atuar em caracter emergencial, conforme descrito na seção How SoftExpert treat vulnerabilities issues do documento SoftExpert Cloud Infrastructure.', new_x="LMARGIN", new_y="NEXT")
  pdf.multi_cell(190, 10, f'  Com base nos relatórios atualizados, não existem riscos graves que possam comprometer a Segurança da informação do ambiente Cloud.', new_x="LMARGIN", new_y="NEXT")
  
# Mount PDF
pdf.print_chapter('', '', capa)
pdf.print_chapter(1, 'Introdução', introducao)
pdf.print_chapter(2, 'Ferramentas Utilizadas', ferrUtilizadas)
pdf.print_chapter(3, 'Relatorio ISO 27001', relOrca27001)
pdf.print_chapter(4, 'Alertas de vulnerabilidades', relOrcaAlerts)
pdf.print_chapter(5, 'Relatorio  AWS Foundational Security Best Practices', relAwsFundation)
pdf.print_chapter(6, 'Parecer Final', parecerFinal)

# Save PDF
pdf.output('hardning-report.pdf')

# Save in S3
s3 = boto3.resource('s3')
BUCKET = 'reports-cloud-softexpert'

s3.Bucket(BUCKET).upload_file('hardning-report.pdf', f'hardening-report-{current_datetime}.pdf')
