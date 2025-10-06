import type { Conversation } from "../../app/core/dashboard";
import { useOutletContext } from "react-router";

export default function MonitorConversation() {
  const { conversation } = useOutletContext<{ conversation: Conversation }>();

  return (
    <div className="[95%] max-w-4xl mx-auto flex flex-col items-start space-y-4 p-4">
      <h2 className="text-2xl font-bold">Conversation Analysis</h2>
      <a
        href={`/conversation/${conversation.id}/analysis`}
        className="underline"
      >
        <button className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
          View Analysis
        </button>
      </a>
    </div>
  );
}
