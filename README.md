## General Information
This project simulates the how market data flows from exchange to the client. A server will read a dummmy file that contains market data in their native protocol and sends it through a TCP connection through RabbitMQ 's topic exchange. Another client application will receive the data and trys to build the book, the book state is then published over the another TCP connection to any client subscribing to the market data to display a dart board. This project still lacks a frontend UI that is fast enough to handle large volume of data and rendering them at the same time.

## Motivation
This is to practice on  using rabbitmq as the exchange to publish and receive data via topic exchange. It is serve as a practice for C++ application using Qt6. Turns out that rabbitmq consumer is not compatible with Qt6 and it leads to some issue. Hence, This has become a practice for C# WPF application instead. The WPF product is not ready yet.

## Technology Used
- python 3.9
- rabbitmq 3.7.8

## Features
- Process market data from market protocol to usable format.
- the data is then published through the network via a messaging broker to be listened to by a client.
- client code will interpret the message and then build the book to display book order status, market status, last trade.
- the orderbook has the ability to combine normal orders and special orders to give a more reasonable view of the market.

## Running The Code
Consumer has to start first before the Publisher as the publisher does not have snapshot capability yet.

- Use the requirements.txt files to install the required python packages using `pip install -r requirements.txt`
- `python server/main.py --date YYYYMMDD` to start server.
- `python client/main.py` to start client.

## Future Extension
C# client to do matching for a more efficient program and combine with the WPF application for a proper user interface.



