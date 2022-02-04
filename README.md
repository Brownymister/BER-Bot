# BER bot

![](/md_file.png)

<div align="center">

  <a href="">![GitHub last commit](https://img.shields.io/github/last-commit/Brownymister/BER-Bot?color=blue&style=plastic)</a>
  <a href="">![GitHub](https://img.shields.io/github/license/Brownymister/BER-Bot?style=plastic)</a>
  <a href="">![Twitter Follow](https://img.shields.io/twitter/follow/BERAirport_Bot?style=social)</a>

</div>

Twitter bot that tweets departures and arrivals from Berlin-Brandenburg airport. It uses the opensky-api. 

Twitter: [@BERAirport_Bot](https://twitter.com/BERAirport_Bot)

I use the /api/states/all endpoint from opensky-network.org because the departures and arrivals data by airport are calculated only in the night for the previous day. The track by flight endpoint can't be used either, because the endpoint is inactive. 

Opensky-API: [https://openskynetwork.github.io/opensky-api/](https://openskynetwork.github.io/opensky-api/)