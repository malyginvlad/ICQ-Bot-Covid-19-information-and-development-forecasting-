# ICQ-Bot-Covid-19-information-and-development-forecasting-

Description of bot functionality:
    
News feed button: displays basic information about the status and development of COVID19 in Russia according to the data of the stopkoronovirus.ru portal.
The data contains the top 10 news from the site and is updated every time the button is called.

Button "Forecast for the development of COVID-19": shows data from the WHO (World Health Organization) and the Yandex portal for today.
Data is updated every day at 11:00 from https://datalens.yandex/covid19.
Next, a graph of indicators of sick, recovered, and mortality rates for the current date and buttons for obtaining a forecast based on data for a different period of time (week, month) are displayed.

The forecast model is based on time series analysis. Based on the model of exponential smoothing.
The exponential smoothing and forecasting model belongs to the class of adaptive forecasting methods,
the main characteristic of which is the ability to continuously take into account the evolution of the dynamic characteristics of the studied processes,
adapt to this dynamics, giving, in particular, the greater weight and the higher information value of the available observations,
the closer they are to the current point in time.
A quadratic function was taken as the loss function and its advantage is sign invariance - the value of the function is always positive. regardless of the error sign, the result will be the same.
We minimize the values of the loss function using optimization based on the Nelder-Mead method,
also known as the deformable polyhedron method. This method of unconditional optimization of a function of several variables,
not using a derived function, and therefore easily applicable to nonsmooth or noisy functions.
Button "Precautions": shows what you need to know about coronovirus, recommendations for prevention in life and at work.
Button: "Reference Information": shows the description of the bot.

To start the bot, you must run the following commands:
pip install -r requirements.txt (to install the necessary dependencies)

To run a script to receive data and update the forecast model:
python update_data.py (better install package 'screen' in linux and run into the process as: screen -dmS name python update_data.py)

To start the bot, you must run the command:
python icq_final.py
