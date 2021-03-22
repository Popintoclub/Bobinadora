import sys
import PyQt5
import pandas as pd
from pulp import *
import operator
from PyQt5 import QtWidgets
from excelerror import Ui_MainWindow

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)      
        self.setupUi(self)
        self.boton.clicked.connect(self.excel)
        self.boton1.clicked.connect(self.getxls)
    def getxls(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home/karris/python')
        if filePath != "":
            self.datos=pd.ExcelFile(str(filePath))
            self.combox.addItems(list(self.datos.sheet_names))
            self.df=self.datos.parse(self.combox.currentText())
## ingreso de variables importantes: cantidad de pedidos, valor minimo, valor maximo,
## planilla excel(clientes, columna FTO y columna PED)           
    def excel(self):
        ordenes = int(self.intcortes.toPlainText())
        val_min = 350
        val_max = 383
        E = int(self.E.toPlainText())
        dict_pedidos = {}
        clientes = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho','nueve', 'diez', 'once', 'doce',
                    'trece', 'catorce', 'quince', 'dieciseis', 'diecisiete', 'dieciocho', 'diecinueve', 'veinte', 
                    'veintiuno', 'veintidos', 'veintitres', 'veinticuatro', 'veinticinco', 'veintiseis', 'veintisiete',
                    'veintiocho', 'veintinueve', 'treinta', 'treintaiuno', 'treintaidos', 'treintaitres', 'treintaicuatro',
                    'treintaicinco', 'treintaiseis', 'treintaisiete', 'treintaiocho', 'treintainueve', 'cuarenta']  
        peso = 7000
        
        b = self.df["FTO"][:ordenes]
        d = self.df["SALDO"][:ordenes]
        cliente = self.df["CLIENTE"][:ordenes]
        peso = 7000
        diccionario = {}
        m = sum(d)
## defino la cantidad de bobinas a producir y cantidad de kilos a producir para cada cliente, aca se soluciona
## el error de la division del total es distinto a la division parcial de cada uno de los pedidos ya que se redondea
## el entero, es por eso que lo hago antes de empezar a resolver.

## defino el diccionario siguiente como cliente de clave y valores para fto y kilos a pedir.        
        for i in range(len(cliente)):
            diccionario[cliente[i]] = b[i],d[i]

        bobinas0 = []
        kilos0 = []
        cortes0 = []
        kiloporbob0 = []
        kilosprod0 = []
        valores0 = []
        for i in range(len(d)):
            x = d[i]/((b[i]*(peso/2))/383)
            y = d[i]
            z = b[i]
            k = ((b[i]*(peso/2))/383)
            bobinas0.append(round(x))
            kilos0.append(y)
            cortes0.append(round(z))
            kiloporbob0.append(round(k))
        for i in range(len(cortes0)):
            f = kiloporbob0[i] * bobinas0[i]
            kilosprod0.append(f)
        for i in range(len(cortes0)):
            a = (kilos0[i], kilosprod0[i], bobinas0[i], kiloporbob0[i])
            valores0.append(a) 
## hago el diccionario final con IV(puse numero para que sean distintos), formatos, kg pedidos, kg programados
## y bobinas a producir, esto ultimo es importante ya que la produccion es por unidades de bobinas y se realiza el cambio
## de variable a kg solamente multiplicando por 3500 que es el peso de cada bajada.
        dictutil0 ={"IV":cliente,"formato":cortes0, "Kg pedidos": kilos0, "kg programados":kilosprod0, "bobinas programadas": bobinas0}
## desarrollo el DataFrame para imprimir y exportar a archivo .xlsx asi lo leen en excel.   
        dfutil0 = pd.DataFrame(dictutil0)
        
        print(dfutil0)
## unifico los formatos en un global a partir de la suma de pedidos individuales, es por eso que trabajo con unidades y no kilos
## ya que al redondear puede llegar a faltar o sobrar bobinas.
        pesodeunabobina = []
        for i in b:
            a = i*(peso/2)/383
            pesodeunabobina.append(a)
        bobinas1 = []
        for i in range(len(d)):
            a = d[i]/pesodeunabobina[i]
            bobinas1.append(round(a))
## hago un diccionario general que ordena unifica los formatos, todos los kilogramos que sean del mismo formato van a ser sumados
        dict_pedidos = {}
        for index, key in enumerate(b):
            if key not in dict_pedidos:
                dict_pedidos[key] = d[index]
            else:
                dict_pedidos[key] += d[index]        
        dict_orden = {}
        resultado = sorted(dict_pedidos.items(), key=operator.itemgetter(0))
        for item in resultado:
            nueva_clave = item[0]
            nuevo_valor = item[1]
            dict_orden [nueva_clave] = nuevo_valor
## defino nuevamente los valores para el nuevo diccionario en donde los formatos fueron unificados, es decir que posiblemente
## van a aumentar los kilos y bobins a producir de cada formato
        bobinas = []
        kilos = []
        cortes = []
        kilosprod = []
        kiloporbob = []
        valores = [ ]
        
        for i in range(len(cortes)):
            a = (kilos[i], kilosprod[i], bobinas[i], kiloporbob[i])
            valores.append(a)                                 
        for i in dict_orden:
            a = dict_orden[i]/((i*(peso/2))/383)
            b = dict_orden[i]
            e = ((i*(peso/2))/383)
            c = i
            bobinas.append(round(a))
            kilos.append(b)
            cortes.append(round(c))
            kiloporbob.append(round(e))
        for i in range(len(cortes)):
            f = kiloporbob[i] * bobinas[i]
            kilosprod.append(f)
                     
        bob = []
        num = []
        for i in (range(2,len(cortes)+1)):
            bob.append(cortes[:i])
            num.append(i-1)
        bob.reverse()
        dict_comb = dict(zip(num,bob))
        pedidos = dict(zip(cortes,bobinas))
        print(dict_comb)
        print("La cantidad de formatos es igual a: ", len(cortes))
## encuentro todas las combinaciones posibles en donde la sumatoria de bobinas va a estar entre los valores maximos y minimos 
## asignados (las combinaciones posibles son de 2, 3 y 4 en este ultimo caso solo cuando el menor valor *4 esta entre los valores
        posibles = []
        for u in dict_comb:
            for i in dict_comb[u]:
                if val_min <= max(dict_comb[u]) + i <= val_max:
                    a = (max(dict_comb[u]),i)
                    posibles.append(a)
                for o in pedidos:
                    if val_min <= max(dict_comb[u]) + o + i <= val_max and i <= o:
                        b = (max(dict_comb[u]),i,o)
                        posibles.append(b)
                    
                
        minimo = cortes[0]
        if val_min <= minimo * 3 <= val_max:
            posibles.append((minimo,minimo,minimo))
            
        if val_min <= minimo * 4 <= val_max:
            posibles.append((minimo, minimo, minimo, minimo))
        print(posibles)
            
        
## paysan son las bandas de desecho que se producen, empiezo a definir los parametros para restringir el calculo de la matriz            
        paysan = []
        a = [ ]
        for j in cortes: 
            for i in posibles:       
                a.append(i.count(j))
        b = []
        for i in range(0, len(a), len(posibles)):
            b.append(a[i:i+ len(posibles)])
        for i in posibles:
            if sum(i)<370:
                paysan.append(383-sum(i))
            else:
                paysan.append(0)   
## genero los dataframe en donde las filas son la cantidad de combinaciones posibles calculadas anteriormente y las columnas
## son la cantidad de cortes que hay
        dic_pulp = dict(zip(range(len(cortes)),b))
        dic_pulp['posibles'] = posibles
        dic_pulp['banda'] = paysan
        df = pd.DataFrame(dic_pulp)
        print(df)        


## generacion de diccionarios para empezar a trabajar con Pulp
        problema = LpProblem("Problemacombinacion",LpMinimize)
        posibles = list(df['posibles'])
        banda = dict(zip(posibles, df['banda']))
        ## restricciones para el calculo de optimizacion
        posibles_vars = LpVariable.dicts("posibles", posibles, 0, cat='Integer')
### Función objetivo
        problema += lpSum([banda[i]*posibles_vars[i] for i in posibles]), "banda total de la produccion"
### Funciones secundarias 
        
        if len(cortes) == 40:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
            treintiaidos  = dict(zip(posibles, df[31]))
            treintaitres = dict(zip(posibles, df[32]))
            treintaicuatro  = dict(zip(posibles, df[33]))
            treintaicinco  = dict(zip(posibles, df[34]))
            treintaiseis  = dict(zip(posibles, df[35]))
            treintaisiete  = dict(zip(posibles, df[36]))
            treintaiocho = dict(zip(posibles, df[37]))
            treintainueve  = dict(zip(posibles, df[38]))
            cuarenta  = dict(zip(posibles, df[39]))
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[31], "Minimotreintaidos"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[31]+E, "Máximotreintaidos"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[32], "Minimotreintaitres"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[32]+E, "Máximotreintaitres"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[33], "Minimotreintaicuatro"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[33]+E, "Máximotreintaicuatro"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[34], "Minimotraintaicinco"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[34]+E, "Máximotreintaicinco"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[35], "Minimotreintaiseis"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[35]+E, "Máximotreintaiseis"  
            problema += lpSum([treintaisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[36], "Minimotreintaisiete"
            problema += lpSum([treintaisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[36]+E, "Máximotreintaisiete"  
            problema += lpSum([treintaiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[37], "Minimotreintaiocho"
            problema += lpSum([treintaiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[37]+E, "Máximotreintaiocho"  
            problema += lpSum([treintainueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[38], "Minimotreintainueve"
            problema += lpSum([treintainueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[38]+E, "Máximotreintainueve"  
            problema += lpSum([cuarenta[f] * posibles_vars[f] for f in posibles]) >= bobinas[39], "Minimocuarenta"
            problema += lpSum([cuarenta[f] * posibles_vars[f] for f in posibles]) <= bobinas[39]+E, "Máximocuarenta"
        if len(cortes) == 39:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
            treintiaidos  = dict(zip(posibles, df[31]))
            treintaitres = dict(zip(posibles, df[32]))
            treintaicuatro  = dict(zip(posibles, df[33]))
            treintaicinco  = dict(zip(posibles, df[34]))
            treintaiseis  = dict(zip(posibles, df[35]))
            treintaisiete  = dict(zip(posibles, df[36]))
            treintaiocho = dict(zip(posibles, df[37]))
            treintainueve  = dict(zip(posibles, df[38]))
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[31], "Minimotreintaidos"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[31]+E, "Máximotreintaidos"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[32], "Minimotreintaitres"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[32]+E, "Máximotreintaitres"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[33], "Minimotreintaicuatro"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[33]+E, "Máximotreintaicuatro"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[34], "Minimotraintaicinco"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[34]+E, "Máximotreintaicinco"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[35], "Minimotreintaiseis"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[35]+E, "Máximotreintaiseis"  
            problema += lpSum([treintaisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[36], "Minimotreintaisiete"
            problema += lpSum([treintaisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[36]+E, "Máximotreintaisiete"  
            problema += lpSum([treintaiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[37], "Minimotreintaiocho"
            problema += lpSum([treintaiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[37]+E, "Máximotreintaiocho"  
            problema += lpSum([treintainueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[38], "Minimotreintainueve"
            problema += lpSum([treintainueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[38]+E, "Máximotreintainueve"  
            
        if len(cortes) == 38:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
            treintiaidos  = dict(zip(posibles, df[31]))
            treintaitres = dict(zip(posibles, df[32]))
            treintaicuatro  = dict(zip(posibles, df[33]))
            treintaicinco  = dict(zip(posibles, df[34]))
            treintaiseis  = dict(zip(posibles, df[35]))
            treintaisiete  = dict(zip(posibles, df[36]))
            treintaiocho = dict(zip(posibles, df[37]))
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[31], "Minimotreintaidos"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[31]+E, "Máximotreintaidos"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[32], "Minimotreintaitres"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[32]+E, "Máximotreintaitres"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[33], "Minimotreintaicuatro"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[33]+E, "Máximotreintaicuatro"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[34], "Minimotraintaicinco"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[34]+E, "Máximotreintaicinco"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[35], "Minimotreintaiseis"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[35]+E, "Máximotreintaiseis"  
            problema += lpSum([treintaisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[36], "Minimotreintaisiete"
            problema += lpSum([treintaisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[36]+E, "Máximotreintaisiete"  
            problema += lpSum([treintaiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[37], "Minimotreintaiocho"
            problema += lpSum([treintaiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[37]+E, "Máximotreintaiocho"  
            
        if len(cortes) == 37:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
            treintiaidos  = dict(zip(posibles, df[31]))
            treintaitres = dict(zip(posibles, df[32]))
            treintaicuatro  = dict(zip(posibles, df[33]))
            treintaicinco  = dict(zip(posibles, df[34]))
            treintaiseis  = dict(zip(posibles, df[35]))
            treintaisiete  = dict(zip(posibles, df[36]))
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[31], "Minimotreintaidos"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[31]+E, "Máximotreintaidos"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[32], "Minimotreintaitres"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[32]+E, "Máximotreintaitres"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[33], "Minimotreintaicuatro"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[33]+E, "Máximotreintaicuatro"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[34], "Minimotraintaicinco"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[34]+E, "Máximotreintaicinco"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[35], "Minimotreintaiseis"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[35]+E, "Máximotreintaiseis"  
            problema += lpSum([treintaisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[36], "Minimotreintaisiete"
            problema += lpSum([treintaisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[36]+E, "Máximotreintaisiete"  
            
        if len(cortes) == 36:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
            treintiaidos  = dict(zip(posibles, df[31]))
            treintaitres = dict(zip(posibles, df[32]))
            treintaicuatro  = dict(zip(posibles, df[33]))
            treintaicinco  = dict(zip(posibles, df[34]))
            treintaiseis  = dict(zip(posibles, df[35]))
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[31], "Minimotreintaidos"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[31]+E, "Máximotreintaidos"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[32], "Minimotreintaitres"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[32]+E, "Máximotreintaitres"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[33], "Minimotreintaicuatro"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[33]+E, "Máximotreintaicuatro"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[34], "Minimotraintaicinco"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[34]+E, "Máximotreintaicinco"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[35], "Minimotreintaiseis"
            problema += lpSum([treintaiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[35]+E, "Máximotreintaiseis"  
            
        if len(cortes) == 25:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
            treintiaidos  = dict(zip(posibles, df[31]))
            treintaitres = dict(zip(posibles, df[32]))
            treintaicuatro  = dict(zip(posibles, df[33]))
            treintaicinco  = dict(zip(posibles, df[34]))
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[31], "Minimotreintaidos"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[31]+E, "Máximotreintaidos"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[32], "Minimotreintaitres"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[32]+E, "Máximotreintaitres"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[33], "Minimotreintaicuatro"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[33]+E, "Máximotreintaicuatro"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[34], "Minimotraintaicinco"
            problema += lpSum([treintaicinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[34]+E, "Máximotreintaicinco"
            
        if len(cortes) == 34:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
            treintiaidos  = dict(zip(posibles, df[31]))
            treintaitres = dict(zip(posibles, df[32]))
            treintaicuatro  = dict(zip(posibles, df[33]))
            
           
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[31], "Minimotreintaidos"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[31]+E, "Máximotreintaidos"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[32], "Minimotreintaitres"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[32]+E, "Máximotreintaitres"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[33], "Minimotreintaicuatro"
            problema += lpSum([treintaicuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[33]+E, "Máximotreintaicuatro"
           
        if len(cortes) == 33:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
            treintiaidos  = dict(zip(posibles, df[31]))
            treintaitres = dict(zip(posibles, df[32]))
            treintaicuatro  = dict(zip(posibles, df[33]))
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[31], "Minimotreintaidos"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[31]+E, "Máximotreintaidos"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[32], "Minimotreintaitres"
            problema += lpSum([treintaitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[32]+E, "Máximotreintaitres"
          
        if len(cortes) == 32:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
            treintiaidos  = dict(zip(posibles, df[31]))
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[31], "Minimotreintaidos"
            problema += lpSum([treintaidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[31]+E, "Máximotreintaidos"
            
        if len(cortes) == 31:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
            treintaiuno = dict(zip(posibles, df[30]))
          
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[30], "Minimotreintaiuno"
            problema += lpSum([treintaiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[30]+E, "Máximotreintaiuno"
           
        if len(cortes) == 30:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            treinta = dict(zip(posibles, df[29]))
           
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) >= bobinas[29], "Minimotreinta"
            problema += lpSum([treinta[f] * posibles_vars[f] for f in posibles]) <= bobinas[29]+E, "Máximotreinta"
            
        if len(cortes) == 29:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            veintinueve = dict(zip(posibles, df[28]))
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[28], "Minimoveintinueve"  
            problema += lpSum([veintinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[28]+E, "Máximoveintinueve"
            
        if len(cortes) == 28:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
            veintiocho = dict(zip(posibles, df[27]))
            
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[27], "Minimoveintiocho"
            problema += lpSum([veintiocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[27]+E, "Máximoveintiocho"
            
        if len(cortes) == 27:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
            veintisiete = dict(zip(posibles, df[26]))
                        
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[26], "Minimoveintisiete"
            problema += lpSum([veintisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[26]+E, "Máximoveintisiete"
            
        if len(cortes) == 26:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
            veintiseis = dict(zip(posibles,df[25]))
                        
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[25], "Minimoveintiseis"
            problema += lpSum([veintiseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[25]+E, "Máximoveintiseis"
           
        if len(cortes) == 25:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
            veinticinco = dict(zip(posibles, df[24]))
                       
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[24], "Minimoveinticinco"
            problema += lpSum([veinticinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[24]+E, "Máximoveinticino"
            
        if len(cortes) == 24:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
            veinticuatro  = dict(zip(posibles, df[23]))
                       
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[23], "Minimoveinticuatro"
            problema += lpSum([veinticuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[23]+E, "Máximoveinticuatro"
            
        if len(cortes) == 23:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
            veintitres  = dict(zip(posibles, df[22]))
         
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) >= bobinas[22], "Minimoveintitres"
            problema += lpSum([veintitres[f] * posibles_vars[f] for f in posibles]) <= bobinas[22]+E, "Máximoveintitres"  
            
        if len(cortes) == 22:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
            veintidos  = dict(zip(posibles, df[21]))
         
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) >= bobinas[21], "Minimoveintidos"
            problema += lpSum([veintidos[f] * posibles_vars[f] for f in posibles]) <= bobinas[21]+E, "Máximoveintidos"  
           
        if len(cortes) == 21:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
            veintiuno  = dict(zip(posibles, df[20]))
           
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) >= bobinas[20], "Minimoveintiuno"
            problema += lpSum([veintiuno[f] * posibles_vars[f] for f in posibles]) <= bobinas[20]+E, "Máximoveintiuno"  
                      
        if len(cortes) == 20:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
            veinte  = dict(zip(posibles, df[19]))
          
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) >= bobinas[19], "Minimoveinte"
            problema += lpSum([veinte[f] * posibles_vars[f] for f in posibles]) <= bobinas[19]+E, "Máximoveinte"  
            
        if len(cortes) == 19:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
            diecinueve  = dict(zip(posibles, df[18]))
           
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[18], "Minimodiecinueve"
            problema += lpSum([diecinueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[18]+E, "Máximodiecinueve"
                    
        if len(cortes) == 18:   
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
            dieciocho  = dict(zip(posibles, df[17]))
          
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[17], "Minimodieciocho"
            problema += lpSum([dieciocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[17]+E, "Máximodieciocho"

        if len(cortes) == 17:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
            diecisiete  = dict(zip(posibles, df[16]))
                        
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) >= bobinas[16], "Minimodiecisiete"
            problema += lpSum([diecisiete[f] * posibles_vars[f] for f in posibles]) <= bobinas[16]+E, "Máximodiecisiete"
            
        if len(cortes) == 16:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
            dieciseis  = dict(zip(posibles, df[15]))
                        
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) >= bobinas[15], "Minimodieciseis"
            problema += lpSum([dieciseis[f] * posibles_vars[f] for f in posibles]) <= bobinas[15]+E, "Máximodieciseis"
            
        if len(cortes) == 15:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
            quince  = dict(zip(posibles, df[14]))
                       
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) >= bobinas[14], "Minimoquince"
            problema += lpSum([quince[f] * posibles_vars[f] for f in posibles]) <= bobinas[14]+E, "Máximoquince"
            
        if len(cortes) == 14:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            catorce = dict(zip(posibles, df[13]))
                       
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) >= bobinas[13], "Minimocatorce"
            problema += lpSum([catorce[f] * posibles_vars[f] for f in posibles]) <= bobinas[13]+E, "Máximocatorce"
        
        if len(cortes) == 13:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
            trece  = dict(zip(posibles, df[12]))
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) >= bobinas[12], "Minimotrece"  
            problema += lpSum([trece[f] * posibles_vars[f] for f in posibles]) <= bobinas[12]+E, "Máximotrece"
            
        if len(cortes) == 12:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
            doce  = dict(zip(posibles, df[11]))
                  
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) >= bobinas[11], "Minimodoce"
            problema += lpSum([doce[f] * posibles_vars[f] for f in posibles]) <= bobinas[11]+E, "Máximodoce"
            
        if len(cortes) == 11:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
            once  = dict(zip(posibles, df[10]))
           
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) >= bobinas[10], "Minimoonce"
            problema += lpSum([once[f] * posibles_vars[f] for f in posibles]) <= bobinas[10]+E, "Máximoonce"
 
        if len(cortes) == 10:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
            diez  = dict(zip(posibles, df[9]))
           
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) >= bobinas[9], "Minimodiez"
            problema += lpSum([diez[f] * posibles_vars[f] for f in posibles]) <= bobinas[9]+E, "Máximodiez"
            
        if len(cortes) == 9:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
            nueve = dict(zip(posibles, df[8]))
           
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) >= bobinas[6], "Minimosiete"
            problema += lpSum([siete[f] * posibles_vars[f] for f in posibles]) <= bobinas[6]+E, "Máximosiete"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) >= bobinas[7], "Minimoocho"
            problema += lpSum([ocho[f] * posibles_vars[f] for f in posibles]) <= bobinas[7]+E, "Máximoocho"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) >= bobinas[8], "Minimonueve"
            problema += lpSum([nueve[f] * posibles_vars[f] for f in posibles]) <= bobinas[8]+E, "Máximonueve"
            
        if len(cortes) == 8:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            seis = dict(zip(posibles, df[5]))
            siete = dict(zip(posibles, df[6]))
            ocho = dict(zip(posibles, df[7]))
                      
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) >= bobinas[5], "Minimoseis"
            problema += lpSum([seis[f] * posibles_vars[f] for f in posibles]) <= bobinas[5]+E, "Máximoseis"
             
        if len(cortes) == 5:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
            cinco = dict(zip(posibles, df[4]))
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) >= bobinas[4], "Minimocinco"
            problema += lpSum([cinco[f] * posibles_vars[f] for f in posibles]) <= bobinas[4]+E, "Máximocinco"
                  
        if len(cortes) == 4:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            cuatro = dict(zip(posibles, df[3]))
         
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) >= bobinas[3], "Minimocuatro"
            problema += lpSum([cuatro[f] * posibles_vars[f] for f in posibles]) <= bobinas[3]+E, "Máximocuatro"

        if len(cortes) == 3:
            uno = dict(zip(posibles, df[0]))
            dos = dict(zip(posibles,df[1]))
            tres = dict(zip(posibles, df[2]))
            
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) >= bobinas[0], "Minimouno"
            problema += lpSum([uno[f] * posibles_vars[f] for f in posibles]) <= bobinas[0]+E, "Máximouno"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) >= bobinas[1], "Minimodos"
            problema += lpSum([dos[f] * posibles_vars[f] for f in posibles]) <= bobinas[1]+E, "Máximodos"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) >= bobinas[2], "Minimotres"
            problema += lpSum([tres[f] * posibles_vars[f] for f in posibles]) <= bobinas[2]+E, "Máximotres"

         
            
## Interpretacion y resolucion de la matriz a partir de las restricciones del problema
        resultado  = {}
        problema.writeLP("SimplecombProblem.lp")
        problema.solve()
        resultado = []
        cantidad = []
        print("Status:", LpStatus[problema.status])
        print("La combinacion balanceada óptima(menor banda), donde cada unidad equivale a 1 comb, consiste de\n"+"-"*110)
        for v in problema.variables():
            if v.varValue>0:
                resultado.append(v.name)
                cantidad.append(int(v.varValue))
        peso_banda = (value(problema.objective))*peso/2/383
        kilos = 'la cantidad de banda producida es :' ,round(peso_banda,2), 'kg'
        kilos_st = str(kilos)
        n = (peso_banda * 100 ) / m
        print("El total de kg producidos : ", round(m+peso_banda,2) , "kg")
        print("El total de banda producida es de: ", round(peso_banda,2), "kg")
        print("El porcentaje de banda producida es de: ", round(n,2), "%")
## convierto de archivo lp a una lista de int para poder manipular los datos introduciendo la pasta a cada corte
## luego los convierto a str para exportar a excel
        povarval = []
        povarkeys = []
        for i in posibles_vars:
            povarval.append(str(posibles_vars[i]))
            povarkeys.append(i)
        dic = dict(zip(povarkeys,povarval))
        
        claves = []
        def clave(dic, value):
            return [key for key, val in dic.items() if val == value]
        for i in resultado:  
            keys = clave(dic, i)
            claves.append(keys)
        pastas = []
        for i in range(len(claves)):
            if sum(claves[i][0])<370:
                pastas.append(383-sum(claves[i][0]))
            else:
                pastas.append(0)  
        a = []
        for i in range(len(claves)):
            a.append(list(claves[i][0]))
        for i in range(len(claves)):
            claves[i].append(pastas[i])
        lista = []
        for i in range(len(claves)):
            a = claves[i][0]
            b = list(a)
            lista.append(b)
        pastas
        for i in range(len(claves)):
            lista[i].append(pastas[i])
        cantidad1 = []
        for i in range((len(cantidad))):
            cantidad1.append(cantidad[i]*3500)
        #for i in range(len(cantidad1)):
            #print(lista[i], "=", cantidad1[i])
        lista4 = []
        for i in lista:
            a = str(i)
            lista4.append(a)
        diccionariofinal = {"Cortes":lista4, "cantidad":cantidad1, "bajadas":cantidad}
        dffinal = pd.DataFrame(diccionariofinal)
        print(dffinal)
        dic_solucion = dict(zip(lista4,cantidad))
        sumvariables = []
        listafinal = []
        
## exportar a excel los dataframe resultado        
       # dffinal0excel = dfutil0.to_excel("tabla.xlsx")
       # dffinalexcel = dffinal.to_excel("programa.xlsx")
        
if __name__ == "__main__":
    dirname = os.path.dirname(PyQt5.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    QtWidgets.QApplication.addLibraryPath(plugin_path)
    app =  QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
