let channel;

new window.QWebChannel(window.qt.webChannelTransport, (_channel) => {
    channel = _channel;
    console.log("Acquired RPC channel");
});

export async function sendMessage(text: Record<string, unknown>): Promise<Record<string, unknown>> {
    if (channel) {
        return await channel.objects.handler.send(text);
    }
    return Promise.reject();
}
