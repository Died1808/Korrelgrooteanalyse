import sys
import pandas as pd
import numpy as np

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

pd.set_option('display.max_columns', 10) 
pd.options.display.width=None
pd.set_option('display.max_rows', None) 
pd.set_option('display.expand_frame_repr', True)
pd.options.display.float_format = '{:,.2f}'.format

out=pd.DataFrame(columns = [['nr','naam', 'x', 'y', 'diepte m NAP', 'D5','D10','D15','D17','D20','D25',
 'D30','D35','D40','D45','D50','D55','D60','D65','D70','D75','D80','D85','D90',
 'D95','D100', 'k_Haazen','k_Sauerbrei','k_Pavchich','k_Seelheim','k_CarKoz','k_Alysen','k_Bedinger',
 'k_Terzaghi','k_Harleman','k_DenRooij','k_Beyer','k_KCB','k_KCU', 'Cu','Io', 'k_mediaan','k_mean']])


"""
Vaste waarden
Hieronder staan een aantal door de verschillende doorlatendheidsberkeningen
gehanteerde constantes

"""
Por  =	0.3
g	 =	9.81
Vorm = 1.25
Porget	 =	Por/(1-Por)
diwa12gr = 999.5
Dynvis   = 0.001234
Kinvis   = 0.0000012346
Corfact  = 0.4 ## 0.81 cf excelsheet maar dan ligt alles een factor 2 te hoog
Ck       = 8.3E-3

"""
Data bewerken
Voor het bewerken van de data wordt een (geanominiseerde in dit voorbeeld) excel tabel uitgelezen waarbij het script
rekening houdt met lege cellen in de matrix. Er mogen dus korrelgroottemetingen ontbreken.
Vervolgens wordt voor elke regel in de tabel de verschillende Dxx waarden berekend en
de bijbehorende doorlatendheden. Tenslotte wordt er weer een exceltabel gemaakt met 
de verschillende parameters en doorlatendheden

"""
matori=pd.read_excel('KGA_test.xlsx', engine='openpyxl')
lenmat = len(matori)
mat=pd.read_excel('KGA_test.xlsx', engine='openpyxl').T
mat=mat.replace(',','.')

for k in range(1,lenmat,1):
    df = pd.DataFrame()    
    
    mat0= mat.iloc[:,[k]].copy()
    naam = mat0.iloc[0,0]   
    x=mat0.iloc[1,0]
    y=mat0.iloc[2,0]
    mid = round(mat0.iloc[4,0],2)
    
    mat0= mat0.iloc[5:]
    mat0.columns =['perc']
    mat0=mat0.dropna()
    Dxklasse = []
    Dxwaarde = []
   
    for D10 in [5,10,15,17,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]:
        Dxklasse.append(D10)
        
        mat0['a'] = np.where(mat0['perc'] <D10, mat0['perc']/100, 0)
        mat0['b'] = np.where(mat0['perc'] >D10, mat0['perc']/100, 2)
        mat0['a'] = pd.to_numeric(mat0.a, errors='coerce')
        mat0['b'] = pd.to_numeric(mat0.b, errors='coerce')
        
        d10a = mat0['a'].max()
        d10b = mat0['b'].min()

        try:
            if d10a != 0.0:
                d10ar = mat0['a'].idxmax()/1000
            else:
                d10ar =0
            d10br = 2/1000
            d10br = mat0['b'].idxmin()/1000
            
        except (ValueError, TypeError):
            pass

        if D10==100:
            d10ar=d10ar
            d10br = 31.5
            
        Dx_mm=d10ar-((D10/100-d10a)/(d10b-d10a)*(d10ar-d10br))
        Dxval = round(Dx_mm,3)
        Dxwaarde.append(Dxval)
        
    df['Dx'] = Dxklasse
    df['mm'] = Dxwaarde 
    

    Cu     = df.iloc[11,1]/df.iloc[1,1]
    Io     = df.iloc[1,1]-(df.iloc[10,1]-df.iloc[1,1])/4
    
    """
    K-waarden uit diverse formules. 
    Hieronder worden aan de hand van literatuurgegevens de doorlatendheden berekend
    Omdat hier soms een forse spreiding in aanwezig is wordt naast de mean ook de mediaan gehanteerd
    als uiteindelijke waarde. Een aantal (KCB, KCU, Den Rooijen, Beyer) blijken voor deze tabel correctiewaarden
    nodig te heben om ze te laten aansluiten bij de rest van de methodes. Dit moet nog wordne gevalideerd.
    """
    if (3 > df.iloc[1,1] > 0.1) and df.iloc[12,1] <5:
        Hazen = 1000 * df.iloc[1,1]**2 
    else:
        Hazen=np.nan
    
    if (df.iloc[9,1] < 0.5):
        Sauerbrei = g/Kinvis*(0.00375*((Por**3)/(1-Por)**2)*(df.iloc[3,1]**2)*Corfact)
    else:
        Sauerbrei=np.nan
    if (df.iloc[10,1] < 0.5):
        Pavchich = 1200*Corfact*df.iloc[3,1]**2
    else:
        Pavchich=np.nan
    if(df.iloc[10,1] >2):
        Seelheim=np.nan
    else:
        Seelheim = 308*df.iloc[10,1]**2
    if (1 > df.iloc[1,1] > 0.1) and df.iloc[12,1] <5:
        US = 80* df.iloc[4,1]**2.3 # 311 cf excel, maar dan ligt alles een facto r4 te hoog irt de rest
    else:
        US=np.nan
    KCB    = 0.25*Ck*(diwa12gr*g/Dynvis)*(Por**3/(1-Por)**2)*((df.iloc[1,1]**2)) # Delen door 4? om aan te sluiten bij de rest? en hieronder door 5
    KCU    = 0.2*(1/Vorm)*0.417*(Porget**3)/(1+Porget)*((df.iloc[10,1]**2)*((np.exp((-1/8)*np.log(df.iloc[14,1]/df.iloc[2,1]))**2))**2)*3600*24
    if(df.iloc[10,1] >2):
       CarKoz=np.nan
    else:
       CarKoz = (Por**3*df.iloc[10,1])/(36*(1-Por)**2)*3600*24 
    AlySen = 1296*((Io+0.025*(df.iloc[10,1]-df.iloc[1,1]))**2)
    if(df.iloc[10,1] >2):
       Bedinger=np.nan
    else:
       Bedinger = 200*df.iloc[10,1]**2
    Harleman = 0.01157*6.54e-1*(df.iloc[1,1])**2*(24*60*60)
    Terzaghi = 1000*((Por-0.13)**2/((1-Por)**2/3))*df.iloc[1,1]
    DenRooij= 0.1*(1.2e4-1.83e3*np.log(Cu))*df.iloc[1,1]**2 #met de factor 0.1 komt Den Rooijen overeen met de andere methodes. Weet niet waarom
    Beyer = 0.1*(6e-4*g/Kinvis)*np.log10(500/Cu)*df.iloc[1,1]**2 #met de factor 0.1 komt Beyer overeen met de andere methodes. Weet niet waarom 

    """
    Uiteindelijk wordt hieronder alles verwerkt tot een uitvoertabel.
    Op basis van persoonlijke ervaring is voor de k-waarde een selectie uit de 
    verschillende methodes gehaald, dat zal voor andere locaties wellicht anders zijn

    """
    
    K_waarde = [round(Sauerbrei,1), round(Pavchich,1), round(Seelheim,1),
                round(AlySen,1), round(CarKoz,1), round(Bedinger,1), round(Terzaghi,1), round(Harleman,1)]

    out.loc[k] = [k, naam, x, y, mid, *Dxwaarde, round(Hazen,1), round(Sauerbrei,1),
           round(Pavchich,1), round(Seelheim,1), round(CarKoz,1),
           round(AlySen,1), round(Bedinger,1), round(Terzaghi,1), round(Harleman,1),
           round(DenRooij,1), round(Beyer,1), round(KCB,1), round(KCU,1), round(Cu,1), round(Io,1),
           round(np.nanmedian(K_waarde),1),round(np.nanmean(K_waarde),1)]

out.to_excel('k_waarde_test.xlsx')







































