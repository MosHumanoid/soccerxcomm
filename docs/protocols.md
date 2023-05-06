# Protocols

The communication protocol is divided into two parts: control and image transmission.

In control, both the client and server serialize information in JSON format for transmission to ensure reliability. The specific serialization format can be found in the [repository](https://github.com/MosHumanoid/SDK/blob/main/protocols/schemas).

For image transmission, the RTSP protocol is used. The server encodes image data in JPEG format for transmission to ensure speed.
