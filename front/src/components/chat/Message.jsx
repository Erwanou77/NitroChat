const Message = ({ message }) => {
  const isOutgoing = message.sender === 'me';

  return (
    <div className={`flex mb-4 ${isOutgoing ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-[70%] rounded-lg p-3 ${
          isOutgoing ? 'bg-indigo-500 text-white' : 'bg-white text-gray-800'
        }`}
      >
        <p className="break-words">{message.message}</p>
        <span className={`text-xs ${isOutgoing ? 'text-indigo-100' : 'text-gray-500'} block mt-1`}>
        </span>
      </div>
    </div>
  );
};

export default Message;