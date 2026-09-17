// Add a UI that looks like a basic chat window (a message history area and an input box at the bottom).

const ChatPage = () => {
    return (
        <div className="w-full">
            <h1 className="text-2xl font-bold w-full">Chat</h1>
            <div className="w-full flex flex-col items-center mt-4">
                <div className="border border-gray-200 rounded-lg p-4 mt-4">
                    <p>Chat with your documents</p>
                    <p>Chat with your documents</p>
                </div>
                <form className="w-full flex mt-4">
                        <input type="text" placeholder="Message" className="w-full border border-gray-200 rounded-lg p-2" />
                    <button type="submit">Send</button>
                </form>
            </div>
        </div>
    );
};

export default ChatPage;