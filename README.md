# Weather
## Описание и функционал
Веб-приложение для прогноза погоды. Предполагаются регистрация и вход. У каждого пользователя есть свой набор выбранных им мест, для прогноза погоды. Он может редактировать этот набор. Также он может загружать данные прогноза для определённого места в формате txt, json. 
## Архитектура
Примерная диаграмма классов:
![weather class diagram](https://github.com/artlvruran/WeatherWeb/blob/documentation/diagrams/weather%20Class%20diagram.png)
1. User - класс представления пользователя в БД
2. WeatherCard - класс представления погодной карточки в БД
3. Coords - класс географических координат
4. Weather - класс собственно прогноза погоды
5. Place - класс представления прогноза погоды для данного города
