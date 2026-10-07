// Temporary reproduction tests for upstream bug reports (not part of any patch).
#include "doip/common/DoIpConnectionHandlerMock.h"
#include "doip/common/DoIpTcpConnection.h"

#include <async/AsyncMock.h>
#include <async/TestContext.h>
#include <tcp/socket/AbstractSocketMock.h>

#include <etl/array.h>
#include <gmock/gmock.h>

namespace
{
using namespace ::testing;
using namespace ::doip;

struct ReproTest : Test
{
    ReproTest() : asyncContext(1U), testContext(asyncContext) {}
    void SetUp() override { testContext.handleAll(); }
    NiceMock<::async::AsyncMock> asyncMock;
    ::async::ContextType asyncContext;
    ::async::TestContext testContext;
    NiceMock<::tcp::AbstractSocketMock> socket;
    StrictMock<DoIpConnectionHandlerMock> handler;
};

// Finding 1: the discard continuation for a message with an empty payload (alive check
// request) leaves the connection unable to read the next message.
TEST_F(ReproTest, DiscardContinuationWithEmptyPayloadStopsReception)
{
    ::etl::array<uint8_t, 8U> writeBuffer;
    DoIpTcpConnection connection(asyncContext, socket, writeBuffer);
    (void)socket.readImplementation(nullptr, 0U); // see finding 3
    ON_CALL(socket, read(_, _)).WillByDefault(Invoke(&socket, &::tcp::AbstractSocketMock::readImplementation));
    ON_CALL(socket, isEstablished()).WillByDefault(Return(true));
    connection.init(handler);
    uint8_t const aliveCheckRequest[] = {0x02, 0xFD, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00};
    uint8_t const nextHeader[]        = {0x02, 0xFD, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00};
    EXPECT_CALL(handler, headerReceived(_))
        .WillOnce(Return(IDoIpConnectionHandler::HeaderReceivedContinuation{
            IDoIpConnection::PayloadDiscardedCallbackType{}}))
        .WillOnce(Return(IDoIpConnectionHandler::HeaderReceivedContinuation{
            IDoIpConnectionHandler::HandledByThisHandler{}}));
    (void)socket.inject(aliveCheckRequest);
    (void)socket.inject(nextHeader); // expected: second headerReceived(); observed: none
}

// Finding 3: inject() before any read copies from a null read window.
TEST(ReproMockTest, InjectBeforeAnyReadReadsFromNull)
{
    NiceMock<::tcp::AbstractSocketMock> socket;
    uint8_t const data[] = {1, 2, 3};
    uint8_t buffer[3]    = {};
    socket.inject(data);
    EXPECT_EQ(3U, socket.readImplementation(buffer, 3U)); // crashes: mem_copy from nullptr
}
} // namespace
