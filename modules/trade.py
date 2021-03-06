# -*- coding: utf-8 -*-

import time, datetime, sys
import urllib2
from core import calculos
from wrappers import poloniex
import llamadas, trade_layer, avisos, config, funcionamiento, wifi_conexion

base = llamadas.Base_datos()
api = poloniex.poloniex(config.keypublic, config.keysecret)

def venta():
    moneda = str(base.mostrar_moneda())
    soporte_min = float(base.mostrar_margen('soporte', 'minimo'))
    soporte_max = float(base.mostrar_margen('soporte', 'maximo'))
    soporte_inicial = calculos.media(soporte_min, soporte_max)     # Calcula el soporte inicial para actualizar la primera subida de stoploss
    total_compra = api.returnTradeHistory('BTC_' + moneda)[0]['total'] # Cogemos el precio al que compramos
    cantidad_compra = api.returnTradeHistory('BTC_' + moneda)[0]['amount']
    precio_compra = api.returnTradeHistory('BTC_' + moneda)[0]['rate']
    precio = llamadas.precio(moneda, 'bids')['precio']
    print 'DEP: Obtenemos las constantes de venta'
    if base.mostrar_checkpoint() is None:
        base.insertar_checkpoint(precio_compra)
        print 'DEP: Insertamos en la base el primer checkpoint y entramos al bucle de venta' # Inserta en la base el checkpoint donde estamos (1)
    else:                            # a no ser que ya exista un check_actual
        pass
    while float(base.mostrar_stoploss()) < float(precio):  # Mientras no salte el stop loss (movil o de protección)
        try:
            precio_mercado = llamadas.precio(moneda, config.vender)['precio'] # Cogemos el precio de compras
            precio_maximo = trade_layer.calc_precio_maximo(precio_mercado)
            print 'Precio de mercado: ' + str(precio_mercado) + ', compraste a ' + str(precio_compra) + ', Checkpoint: ' + str(base.mostrar_checkpoint())
            if float(str(precio_mercado)) > float(base.mostrar_checkpoint()): # Si el precio de mercado es mayor que el checkpoint actual
                base.actualizar_stoploss(str(trade_layer.subir_stoploss(precio_maximo)))
                stop_loss = base.mostrar_stoploss()
                base.actualizar_checkpoints(trade_layer.calc_precio_maximo(precio_maximo))
                precio = precio_mercado
                print 'DEP: Subimos el stop_loss a ' + str(stop_loss)
            if config.enviar_mails_checkpoint:
                venta_total_stop_loss = (float(stop_loss) * float(cantidad_compra)) - (float(stop_loss) / 400)
                avisos.ganancia_relativa(str(venta_total_stop_loss), str(total_compra))
                print 'DEP: Avisamos por mail de la ganacia relativa '
            else:
                pass
            llamadas.venta(base.mostrar_moneda(), llamadas.precio(base.mostrar_moneda(), config.vender), float(llamadas.balance(base.mostrar_moneda(), 'available')))
            precio = precio_mercado
            print 'DEP: actualmente tenemos {0} de ganancia per mBTC, esperamos {1} segundos'.format(
                "{0:.3f}".format((float(precio_mercado) - float(precio_compra))*1000) +
                ' (' + "{0:.2f}".format(100 * (float(precio_mercado) / float(precio_compra)) - 100) + '%)',
                str(config.espera))
            print 'Stoploss: ' + str(float(base.mostrar_stoploss())), ', Timestamp: {:%d.%m.%Y %H:%M:%S}'.format(datetime.datetime.now())
            print
            time.sleep(int(config.espera))
        except KeyboardInterrupt:
            print 'Vas a detener el proceso de venta'
            print 'El programa no guardará el stop-loss actual'
            print 'Si deseas guardarlo deberás configurarlo manualmente desde http://www.poloniex.com'
            print
            funcionamiento.pausar_trade_venta()
    if float((llamadas.precio(moneda, config.vender))['precio']) < float(base.mostrar_stoploss()):  # Que la venta haya caído por debajo del stop loss de protección
        print 'DEP: El precio ha caído por debajo del stoploss de protección'
        venta_successful = False
        while not venta_successful:
            try:
                respuesta = llamadas.venta(base.mostrar_moneda(), str((llamadas.precio(base.mostrar_moneda(), config.vender))['precio']), float(llamadas.balance(base.mostrar_moneda(), 'available'))) # Vende desesperadamente a precio de compra
                id_venta = respuesta['orderNumber']
                venta_successful = True
            except TypeError:
                venta_successful = False
                pass
    print 'DEP: Esperamos 5 segundos a que el servidor procese la orden'
    time.sleep(5)       # Duerme 5 segundos para que el servidor procese la orden
    estado = 'en_proceso'
    while estado == 'en proceso':
        try:
            api.returnOpenOrders('BTC_' + moneda)[0]  # Si hay orden abierta todavía
            print 'DEP: La orden sigue abierta, esperamos 7 segundos'
            time.sleep(7)           # Esto se hace para evitar que la venta no se haya cumplido por bajadas fuertes del mercado
            try:
                api.returnOpenOrders('BTC_' + moneda)[0]   # Si tras 7 segundos no se ha vendido
                print 'DEP: Aún no se ha vendido, cancelamos la orden volvemos a lanzar la función de venta'
                api.cancel('BTC_' + moneda, str(id_venta))
                venta()
            except IndexError:
                estado = 'vendido'
        except IndexError:
            estado = 'vendido'
    print 'DEP: La venta se ha realizado'
    if config.enviar_mails_operacion:
        informacion = llamadas.ultimo_trade(moneda)     # Cogemos la información de la venta
        avisos.operacion(informacion)            # Avisamos al correo de la venta efectuada
        print 'DEP: Enviando mail de aviso de venta'
    else:
        pass
    print 'DEP: LA DEPURACION DE LA VENTA SE HA COMPLETADO CORRECTAMENTE'
    if config.reiniciar:                               # Comprobamos si está el reinicio automático activado
        print 'DEP: El reinicio automático está activado, así que volvemos a comprar'
        organizador()
    else:
        print 'El reinicio automático esta desactivado, cerrando el programa...'
        print '¡Hasta la próxima!'
        base.cerrar()   # Cerramos la base de datos
        sys.exit(0)

#Bucle de compra
def compra():
    moneda = str(base.mostrar_moneda())
    print 'DEP: Obtenemos las constantes de compra'
    estado = 'en_proceso'
    while estado == 'en_proceso':
        try:
            if calculos.rango(str(llamadas.precio(moneda, config.comprar)['precio']), base.mostrar_margen('soporte', 'minimo'), base.mostrar_margen('soporte', 'maximo')) == True:  #Si el precio de venta/compra actual está en el rango de soporte
                print 'DEP: El precio de ' + moneda + ' (' + str(llamadas.precio(moneda, 'asks')['precio']) + ') está en el rango de soporte, intentamos comprar'
                cantidad = (float(llamadas.balance('BTC', 'available'))) / (float(llamadas.precio(moneda, config.comprar)['precio']) + 0.00000001)  # La cantidad que vamos a comprar
                try:
                    respuesta = api.returnOpenOrders('BTC_' + moneda)[0]
                except IndexError:
                    # Significa que no hay ordenes abiertas
                    pass
                try:
                    id_compra = str(respuesta['orderNumber'])
                    print 'DEP: La compra esta abierta, la id es :' + str(id_compra)
                except (IndexError, KeyError, UnboundLocalError):
                    respuesta = api.buy('BTC_' + moneda, str(float(llamadas.precio(moneda, config.comprar)['precio']) + 0.00000001), str(cantidad))   #Compramos a precio de compra y nos quedamos con la id de la transacción
                    try:
                        id_compra = str(respuesta['orderNumber'])
                        print 'DEP: Abrimos la compra a ' + str(api.returnOpenOrders('BTC_' + moneda)[0]['rate']) + ', la id es :' + str(id_compra)
                    except (IndexError, KeyError, TypeError):
                        pass
                if llamadas.orden_abierta(moneda):    #Mientras haya una orden abierta
                    print 'DEP: Esperamos  ' + str(config.espera) + ' segundos a que la compra se efectúe'
                    time.sleep(config.espera)                          #Espera 30 segundos y repite el bucle hasta que ya no haya orden abierta
                    if llamadas.orden_abierta(moneda):      # Si tras ese tiempo sigue abierta
                        print 'Cancelamos la compra y volvemos a empezar'
                        api.cancel('BTC_' + moneda, str(id_compra))      # Cancélala y vuelve a empezar el bucle
                        compra()
                    else:
                        pass
                else:
                    pass
                print 'DEP: La compra se ha efectuado'
                estado = 'comprado'
            else:                       #Si el precio de venta actual no está en el rango de soporte
                print 'El precio de compra actual de ' + moneda + ' no está en el rango de soporte (' + str(llamadas.precio(moneda, config.comprar)['precio']) + ' BTC)'
                print 'El Boto Grande intentará comprar cuando llegue, ten paciencia...'
                print
                if not calculos.rango(str(llamadas.precio(moneda, config.comprar)['precio']),
                                      base.mostrar_margen('soporte', 'minimo'),
                                      base.mostrar_margen('soporte', 'maximo')):
                    time.sleep(5)          #El programa duerme 5 segundos y vuelve a empezar el bucle While, para intentar de nuevo la compra
                    compra()
        except KeyboardInterrupt:
            print 'Vas a detener el proceso de compra'
            print
            funcionamiento.pausar_trade_compra()
    informacion = llamadas.ultimo_trade(moneda)     # Cogemos la información de la compra
    print 'DEP: Cogemos la información de la compra'
    avisos.operacion(informacion)       # Avisamos al correo de la compra efectuada
    print 'DEP: Avisamos al correo de la compra efectuada'
    print 'DEP: Aquí lanzaríamos la función de venta'
    print
    print 'LA DEPURACION DE COMPRA SE HA COMPLETADO CORRECTAMENTE, PASAMOS AL BLOQUE DE VENTA'
    venta()       #Cuando se rompe el bucle lanzamos la función de venta

# Organiza el estado del programa y envia el trade a su bucle correspondiente
def organizador():
    try:
        base.insertar_id('compra', '0')     # Insertamos los ids de compra y venta en la base
        base.insertar_id('venta', '0')      # Así luego sólo debemos actualizarlos
        moneda = base.mostrar_moneda()
        print 'DEP: El organizador toma la moneda'
        try:
            api.returnOpenOrders('BTC_' + moneda)[0]     # Comprueba que hay una orden abierta, si la hay
            print 'Hay una orden abierta de ' + str(llamadas.tipo_orden(moneda)) + ' de ' + moneda + ' a ' + str(api.returnOpenOrders('BTC_' + moneda)[0]['rate']) + ' BTC'
            if api.returnOpenOrders('BTC_' + base.mostrar_moneda())[0]['type'] == 'buy': # Si es una orden de compra
                print 'DEP: Entramos en la función de compra'
                compra()
            else:
                print 'DEP: Entramos en la función de venta'
                venta()
        except IndexError:          # Si no la hay
            print 'No hay órdenes abiertas'
            if float(llamadas.balance(moneda, 'available')) == 0 and float(llamadas.balance('BTC', 'available')) > config.min_btc:
                print 'DEP: Entramos en la función de compra'
                compra()
            elif float(llamadas.balance('BTC', 'available')) < config.min_btc and float(llamadas.balance(moneda, 'available')) > 0:
                print 'DEP: Entramos en la función de venta'
                venta()
    except urllib2.URLError:
        print 'No se ha podido contactar con Poloniex, comprobando la conexion...'
        conexion = wifi_conexion.red()
        if not conexion:
            print 'Intentando reconectar...'
            print 'Aún no hay un módulo instalado que permita reconectarse a la red'
        else:
            organizador()
# Bucle principal
def trade():
    print '¿Qué quieres hacer?'
    print '1.Comprar - 2.Vender - 3.Dejar elegir al Boto Grande'
    eleccion = raw_input('Inserta un número: ')
    if eleccion == '1':
        compra()
    elif eleccion == '2':
        venta()
    elif eleccion == '3':
        organizador()
    else:
        print 'Te has equivocado de numero'
        trade()

#print llamadas.precio('BTC_' + 'LSK', 'bids')
#print llamadas.balance('MAID', 'available')


