import type { Conversation } from "../../app/core/dashboard";
import { useOutletContext } from "react-router";

export default function ManageDistribution({
}: {
  }) {
  const { conversation } = useOutletContext<{ conversation: Conversation }>();
  return (
    <div className="[95%] max-w-4xl mx-auto">
      <p>
        Friendly Link: {} 
        <a className="underline" href={window.location.origin + "/conversation/" + conversation.user_friendly_link}>
          {window.location.origin + "/conversation/" + conversation.user_friendly_link}
        </a>
      </p>
    </div>
  );
}
