import mechanize

br = mechanize.Browser()
br.open("https://portalsat.plataforma.sat.gob.mx/TransparenciaDonaciones/faces/publica/frmCConsultaDona.jsp")

response = br.response()

br.select_form('publicaConsultaDonaForm')
br.form['publicaConsultaDonaForm:idSelectEjercicioFiscal'] = ['2019']
br.form['publicaConsultaDonaForm:idRfc'] = 'MMA100524UB9'
#br.form['publicaConsultaDonaForm:_idJsp24'].click()
br.submit()
response = br.response()

with open("mechanize_results.html", "w") as f:
    f.write(response.read().decode())
exit()
br.select_form('publicaConDonaDetalleForm')
br['dataTableDonatarias']['0']['_idJsp20'].click()

response = br.response()
print(response.geturl())
