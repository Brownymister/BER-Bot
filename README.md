# BER bot
Twitter bot that tweets departures and arrivals from Berlin-Brandenburg airport. It uses the opensky-api. 

I use the /api/states/all endpoint from opensky-network.org because the departures and arrivals data by airport are calculated only in the night for the previous day. The track by endpoint can't be used either, because the endpoint is inactive. 