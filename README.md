# Anti-cheating-app

Sistema para prevención de fraude en examenes en linea utilizando **python 3.7.4**

## Funcionalidades principales
***
### Detección de procesos no autorizados.

Por medio de el monitoreo de los proceso en ejecuón y una lista de proceso baneados llamada **banned.csv**. Se lleva a cabo un registro **(log)** de las acciones indevidas que el usuario realizo.


### Timing de inicio y finalización de sesión

Se lleva a cabo un registro de la hora de inicio y hora de finalización del examen por medio de la libreria **datetime**. Ademas se registra en el archivo **log** si el archivo completo la preuba en el tiempo establecido.


### Envío de archivo de registro de actividades (log)

Al finalizar la prueba se enviara directamente el archivo log con los resultados de la sesión del usuario y se mostrara cierto nombre de archivo dependiendo de las acciones que haya realizado y el tiempo en que lo haya terminado.

* **00_timestamp**. Indica que el usuario no realizo ninguna acción maliciosa.

* **01_timestamp**. Indica que el usuario ejecuto programas que estan prohibidos.

* **02_timestamp**. Indica que el usuario no completo la prueba a tiempo.

* **03_timestamp**. Indica que el usuario ejecuto programas que estan prohibidos y ademas no completo la prueba a tiempo.


## GUI
***
La interfaz de usuario cuenta con dos ventanas:

* **Ventana de inicio de prueba por medio de codigo**.

* **Ventanta de administración y control del inicio de la prueba.**


Asi mismo la ventana de administración de la prueba cuenta con tres botones.

* **Botón para inicio de la prueba**. Permite iniciar la prueba ademas de iniciar el cronometro para revizar el tiempo de la prueba

* **Botón para subir el entregable a schoology**. Abre un **secure browser** para hacer la entrega del archivo a la plataforma schoology.

* **Botón para finalizar la prueba**. Finaliza la prueba  y el cronometro. Envia el archivo del **log** a el profesor.

