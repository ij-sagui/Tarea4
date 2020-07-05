# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 16:44:19 2020

@author: Isaí Saborío Aguilar
"""

import pandas as pd
from scipy import stats
from scipy import signal
from scipy import integrate
import matplotlib.pyplot as plt
import numpy as np

'''
Punto 1
Esquema de modulación BPSK
'''
#bits
bits=np.array(pd.read_csv('bits10k.csv',header=None))

#frecuencia de operación.
f=5000 #Hz

#Periodo
T=1/f

#Número de puntos de muestreo
p=50

#puntos de muestreo
tp=np.linspace(0,T,p)

#forma de onda portadora
sen=np.sin(2*np.pi*f*tp)

#Puntos en el tiempo para la señal transmitida
t=np.linspace(0,len(bits)*T,len(bits)*p)

#señal modulada Tx
señal=np.zeros(t.shape)

#señal modulada BPSK
for i, j in enumerate(bits):
    if j==1:
        señal[i*p:(i+1)*p]= sen
    else:
        señal[i*p:(i+1)*p]= -sen

#Graficación de Tx
plt.plot(señal[0:5*p])        
plt.title('Primeros bits modulados de Tx')
plt.grid('true')        
plt.xlabel('t [s]')
plt.ylabel('Amplitud')
plt.savefig('Tx')


'''
Punto 2
Potencia promedio
'''
#potencia instantánea
Pinst=señal**2

#Potencia promedio
Pprom=integrate.trapz(Pinst,t)/(len(bits)*T)
print('La potencia promedio es Pprom={0}'.format(Pprom))


'''
Punto 3
Simulación de canal ruidoso
'''
Pseñal=Pinst

#vector con diferentes valores de SNR entre -2 y 3
SNR=np.linspace(-2,3,6)

#vector de señales recibidas
Rxs=[]

#Creación de las señales después de cada canal ruidoso segun el SNR
for t in SNR: #para recorrer cada valor de SNR
    Pruido=Pseñal / (10**(t/ 10))
    sigma=np.sqrt(Pruido)
    ruido=np.random.normal(0, sigma, señal.shape)
    Rxs.append(señal+ruido) #Señal con ruido que cambia según el SNR aplicado
        
#ejemplo de una de las señales después del canal    
plt.figure()
plt.plot(Rxs[2][0:5*p])        
plt.title('Primeros bits de Rx para SNR=0')
plt.grid('true')        
plt.xlabel('t [s]')
plt.ylabel('Sxx')
plt.ylabel('Amplitud')
plt.savefig('Rx')


'''
Punto 4
Grafica de la densidad espectral de la potencia
'''
fs=p/T #frecuencia de muestreo

# Antes del canal ruidoso
fw, PSD=signal.welch(señal, fs, nperseg=1024)
plt.figure()
plt.grid('true')
plt.semilogy(fw, PSD)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Sxx')
plt.title('Densidad espectral de potencia para Tx')
plt.savefig('PDSTx')

# Después del canal ruidoso
#vector para los nombres de las imagenes que se van a guardar
Nimagenes=['PDSRx-2','PDSRx-1','PDSRx0','PDSRx1','PDSRx2','PDSRx3']

#vector con el título de cada imagen
Ntitulos=['Densidad espectral de potencia para SNR=-2','Densidad espectral de potencia para SNR=-1','Densidad espectral de potencia para SNR=0','Densidad espectral de potencia para SNR=1','Densidad espectral de potencia para SNR=2','Densidad espectral de potencia para SNR=3']

#gráficas después del canal ruidos según el SNR
for t in range(len(Rxs)):    
    fw, PSD=signal.welch(Rxs[t], fs, nperseg=1024)
    plt.figure()
    plt.grid('true')
    plt.semilogy(fw, PSD)
    plt.xlabel('Frecuencia  [Hz]')
    plt.ylabel('Sxx')
    plt.title(Ntitulos[t])
    plt.savefig(Nimagenes[t])

'''
Punto 5
Demodulación y decodificación de la señal

'''

# "Energía de la onda original", se obtiene por la suma 
Es=np.sum(sen**2)
#vector de ceros para los BER correspondientes a cada SNR definido
BER=np.zeros(SNR.shape)

#vector para nombres de errores para el print
Nerrores=['SNR=-2','SNR=-1','SNR=0','SNR=1','SNR=2','SNR=3']

#Generación de BERs
for v in range(len(SNR)):
    bitsRx=np.zeros(bits.shape) #vector de ceros para los bits de Rx
    for a, w in enumerate(bits): #Para calcular cada nuevo vector de bits Rx
        Ep1 = np.sum(Rxs[v][a*p:(a+1)*p] * sen) 
        if Ep1 > Es/2:
            bitsRx[a]=1
        else:
            bitsRx[a]=0
    err=np.sum(np.abs(bits - bitsRx))      
    print('La cantidad de bits erróneos para una relación de señal-ruido {} es de err={}'.format(Nerrores[v],err))
    BER[v]=err/len(bits)


'''
Punto 6
Grafica BER vs SNR
'''
#Generación de gráfica
plt.figure()
plt.plot(SNR,BER)
plt.grid('true')
plt.xlabel('SNR  [dB]')
plt.ylabel('BER')
plt.title('Gráfica BER vs SNR')
plt.savefig('BERvsSNR')