..
   *******************************************************************************
   Copyright (c) 2026 Jefferson Nascimento

   This program and the accompanying materials are made available under the
   terms of the Apache License Version 2.0 which is available at
   https://www.apache.org/licenses/LICENSE-2.0

   SPDX-License-Identifier: Apache-2.0
   *******************************************************************************

..
   AI disclosure: this file was largely generated with an AI assistant and was reviewed by
   the contributor. Assisted-by: Anthropic Claude Opus 5.5

doipClient
==========

Introduction
------------

``doip::DoIpClientTransportLayer`` is the client side of DoIP (ISO 13400-2): it lets an
OpenBSW node act as external test equipment towards other DoIP entities. The ``doip``
module provides the server side, which accepts testers; this module opens connections to
DoIP nodes, activates routing and exchanges diagnostic messages with them.

It is an ``AbstractTransportLayer``, so a transport router can reach Ethernet ECUs in the
same way as CAN ECUs through DoCAN. For example, a diagnostic gateway can forward requests
from its DoIP server to a node behind it:

.. code-block:: none

    tester --DoIP--> DoIpServerTransportLayer --> router --> DoIpClientTransportLayer --DoIP--> node

The module reuses ``doip::DoIpTcpConnection`` and the send jobs of the ``doip`` module for
framing, and any ``tcp::AbstractSocket`` (for example ``tcp::LwipSocket``) for TCP.

Features
--------

- **Connection on demand:** the first message to a node opens a TCP connection to the
  node's address and port, and requests routing activation with the client's logical
  address and activation type ``0x00``. Diagnostic messages are sent after a positive
  activation response (code ``0x10``). The connection is kept for later messages.
- **Delivery confirmation:** a physical message is reported as processed to its
  ``ITransportMessageProcessedListener`` when the node has acknowledged it: positive
  acknowledgement (``0x8002``) as success, negative acknowledgement (``0x8003``) as error.
  The report always waits until the TCP stack has released the message buffer.
- **Delivery budget:** connection set-up, routing activation and acknowledgement must
  complete within a configured time. Otherwise the connection is closed and the message is
  reported as failed. A refused connection or activation and a connection closed by the
  node fail the message at once; the next message connects again.
- **One message per node:** a node takes one physical message at a time; a second one is
  rejected with ``TP_MESSAGE_ALREADY_IN_PROGRESS``.
- **Functional messages:** a message to the configured functional address is sent to every
  node whose routing is active and which has no message in progress. It is reported as
  processed when every copy has been released by TCP.
- **Messages from nodes:** a diagnostic message from a node to the client's address is
  passed to the transport message provider and listener with the node as source. Other
  messages (other target addresses, unknown payload types, wrong protocol version, too large
  payloads) are skipped without losing the stream position.
- **Alive check:** alive check requests of a node are answered with the client's address.
- **Static resources:** connections, sockets and send jobs are allocated with the layer.

Integration Guide
-----------------

- Create a ``doip::declare::DoIpClientTransportLayer<NodeCount, SocketType>`` with the bus
  ID, the parameters, the nodes, the asynchronous context and a millisecond clock, and add
  it to the transport system (for example ``ITransportSystem::addTransportLayer``).
- Call ``send()``, ``cyclic()`` and ``shutdown()`` in the context of the TCP stack (for lwIP,
  the Ethernet task); all socket callbacks arrive in that context.
- Call ``cyclic()`` periodically, for example every 10 ms, for the delivery budget.
- Choose a delivery budget shorter than the supervision of the component that calls
  ``send()``. A router must not reuse a message buffer that the client still sends.
- Each node needs one TCP connection (one ``tcp_pcb`` with lwIP) besides those of the DoIP
  server.

Configuration
-------------

``doip::DoIpClientParameters``:

.. list-table::
   :header-rows: 1

   * - Field
     - Meaning
   * - ``sourceAddress``
     - Logical address of the client; source of all messages and of the routing activation.
   * - ``functionalAddress``
     - Target address that selects the functional message handling.
   * - ``protocolVersion``
     - DoIP protocol version of the generic header, e.g. ``version02Iso2012``.
   * - ``port``
     - TCP port of the nodes, normally ``DoIpConstants::Ports::TCP_DATA`` (13400).
   * - ``deliveryTimeoutMs``
     - Budget from ``send()`` to the node's acknowledgement, including connection set-up.
   * - ``maxPayloadLength``
     - Largest diagnostic message payload accepted from a node.

``doip::DoIpClientNode`` holds the node's logical address, IP address and an optional name
for log output.

Public API
----------

- ``DoIpClientTransportLayer::send()`` sends a message to the node named by its target
  address, or to all nodes for the functional address. ``TP_SEND_FAIL`` means that no
  connection could be started or no node took a functional message; the caller keeps the
  message.
- ``DoIpClientTransportLayer::cyclic()`` supervises the delivery budget.
- ``DoIpClientTransportLayer::connections()`` and ``DoIpClientConnection::state()`` give the
  connection states (``CLOSED``, ``CONNECTING``, ``ACTIVATING``, ``ACTIVE``).

Usage Example
-------------

.. code-block:: cpp

    ::doip::DoIpClientNode const nodes[] = {
        {0x1040U, ::ip::make_ip4(0xC0A8001EU), "ethZone"}};

    ::doip::DoIpClientParameters const parameters{
        0x0E10U, // client address
        0xE400U, // functional address
        ::doip::DoIpConstants::ProtocolVersion::version02Iso2012,
        ::doip::DoIpConstants::Ports::TCP_DATA,
        1500U, // delivery budget in ms
        4095U};

    ::doip::declare::DoIpClientTransportLayer<1U, ::tcp::LwipSocket> client(
        busId, parameters, nodes, ethernetContext, nowMs);

    transportSystem.addTransportLayer(client);
    // every 10 ms in the Ethernet context:
    client.cyclic();

Limitations
-----------

- Plain TCP only; DoIP over TLS is not supported.
- Node addresses are configured; vehicle discovery over UDP is not used.
- One connection per node: several logical addresses behind one DoIP entity need one node
  entry each, and the entity must accept a second routing activation from the same source.
