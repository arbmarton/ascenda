# ascenda

A deployed version can be accessed online at: https://secure-cove-07181.herokuapp.com/. 
The application process goes to sleep after a while, so the first request is going to be slow.
You can query by hotel id in the following way: https://secure-cove-07181.herokuapp.com/hotel_id=id1+id2+...+idn 
and you can query by destination id in the following way: https://secure-cove-07181.herokuapp.com/destination_id=9999 

The application works broadly in the following way:
1. Builds a list of the hotels available in the sources
 - concurrently queries the sources, acquiring all the individual json pieces describing a hotel
 - creates hotel objects, and assigns the aforementioned jsons to them
 - the hotel objects then concurrently parse their own data from the jsons
2. Processes the arguments in the http request
3. Selects the hotels matching the request

The data is returned in the same way as given in the homework description.
