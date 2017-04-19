# -*- coding: utf-8 -*-

# Desde aquí se configura el programa

# INFORMACIÓN PERSONAL
keypublic = "MJPZAO3L-I4U76E7T-RDS6DOJ2-OTIXSYV5"
keysecret = "e2c9757f2b2666f8e8e40cadcd0d04e643cc41ec67d84dbdde2ee4e8cb81b763f2d818e311f0bb27d87c1f6c2495ea1132a32a6836ca63846fa75b307d828e48"

# Path de la base de datos 
ruta_base_datos = '/home/arcsaber/PycharmProjects/elbotogrande/datos/base_datos.db'

#----------------------------------
# Configuracion del mail (Sólo admite gmail)
# Aquí indica si quieres que el bot te envíe mails cuando compre o venda
# Elige entre True o False
enviar_mails_operacion = True

# Aquí indica si quieres que el bot te envíe un mail con la ganancia asegurada cuando supere un checkpoint
# Elige entre True o False
enviar_mails_checkpoint = False

# Aquí indica el mail al cual lo quieres enviar
mail_to = 'carloselsekey@gmail.com'

# Aquí el mail desde donde quieres que envíe los datos
# Recomiendo usar un mail el cual no utilices, así no pones en riesgo la contraseña de tu mail
mail_from = 'elbotogrande@gmail.com'

# Aquí la contraseña del mail desde donde envias la info (mail_from)
contra = '3Lbotogrande'

#-----------------

# INFORMACIÓN DEL BOT (Puramente informativa, no la cambies)
nombre = 'El Boto Grande'
version = '0.1'
#------------------------------------

# CONFIGURACIÓN DE TRADING

# Indica si quieres reiniciar el ciclo automáticamente después de la venta
# AVISO: Se reiniciará intentando comprar en el precio de soporte que pusiste al principio
# Útil para mercados con alta volatilidad y estrategias de rebote (pocos checkpoints, rangos bajos)
reiniciar = True

# Elige si Pythoniex intentará comprar cuando el los precios de venta lleguen al rango de soporte
# o si lo hará cuando los precios de venta lleguen al rango de soporte
# Inserta bids para compra o asks para ventas
comprar = 'bids'
vender = 'bids'

# CONSTANTES DE TRADING

stop_loss = 2   # Porcentaje de pérdida máxima tras la entrada en resistencia

numero_checkpoints = 40     # Cantidad de checkpoints entre el precio de compra y la media de resistencia

# Número entre 0 a 100, es el porcentaje que subirá el stop de venta cada vez que se supere un checkpoint
# El porcentaje se refiere al porcentaje entre el checkpoint anterior y el superado
stop_loss_movil = 99

# Esta variable indica los tiempos de espera en segundos que se detendrá Pythoniex cuando 
# se encuentre en medio del trading
espera = 5


# El minimo de BTC requerido para tradear
min_btc = 0.0005

# AVISO: el programa no está configurado para que venda en la resistencia, si no en el stop movil
# Si quieres que siga subiendo aunque supere la resistencia, simplemente coloca la resistencia más alta
# y mayor cantidad de checkpoints

# SI QUIERES QUE VENDA EN RESISTENCIA COLÓCALA UN POCO MÁS ALTA QUE TU OBJETIVO, ASEGÚRATE DE QUE EL ÚLTIMO
# CHECKPOINT ESTÁ AL NIVEL QUE QUIERES LA RESISTENCIA.
# El rango de resistencia sólo se utiliza para que el programa no calcule checkpoints infinitos

#-----------------

# CONSIDERACIONES GENERALES

# Pythoniex funciona con 1 orden ejecutándose a la vez, es decir que sólo va a funcionar si tienes BTC
# o la moneda que elijas. Inserta BTC en la cuenta de Poloniex o la moneda que elijas.
# Si tienes otra moneda disponible en tu monedero o una orden abierta de venta de esa otra moneda,
# Pythoniex la ignorará, pero por seguridad te recomiendo que abras una cuenta nueva únicamente
# para Pythoniex, en la cual sólo operes con el bot insertando BTC o la moneda que elijas.

# Para más información lee el archivo README.md (en la carpeta principal).

