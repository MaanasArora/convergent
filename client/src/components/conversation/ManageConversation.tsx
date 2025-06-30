import { useEffect, useState } from "react";
import { Conversation } from "../../app/core/dashboard";
import ConversationConfig from "./ConversationConfig";
import { Button } from "@headlessui/react";

export default function ManageConversation({
  editIdItem,
}: {
  editIdItem: Conversation;
}) {
  const [dialogOpen, setDialogOpen] = useState(false);

  const [dialog, setDialog] = useState<HTMLDialogElement | null>(null);

  useEffect(() => {
    const editButton = document.getElementById("edit-button");
    setDialog(document.getElementById("edit-dialog"));
  }, []);

  const handleEditClick = (state) => {
    setDialogOpen(state);
    if (state) {
      dialog?.showModal();
    } else {
      dialog?.close();
    }
  };
  return (
    <>
      <section className="w-[95%] max-w-3xl mx-auto">
        <nav className="breadcrumb">
          <ol className="flex gap-1">
            <li>
              <a href="../../">Dashboard</a>
            </li>
            <li className="before:content-['/']">
              <a href="../" className="pl-1">
                All conversations
              </a>
            </li>
            <li className="before:content-['/']">
              <a href="./" className="pl-1">
                {editIdItem.name}
              </a>
            </li>
            <li className="before:content-['/']">
              <a href="" aria-current="page" className="pl-1">
                Edit
              </a>
            </li>
          </ol>
        </nav>
        <h1 className="text-5xl font-bold mb-8">{editIdItem.name}</h1>
        <button
          id="edit-button"
          className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2"
          onClick={() => handleEditClick(true)}
        >
          Edit
        </button>
        <nav>
          <a>Distribute</a>
          <a>Monitor</a>
          <a>Moderate</a>
        </nav>
      </section>

      <dialog
        id="edit-dialog"
        className="m-[revert] p-[revert] border-2 backdrop:bg-primary backdrop:opacity-80"
      >
        <button
          className="border-2 px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 ml-auto"
          autoFocus
          onClick={() => handleEditClick(false)}
        >
          Close
        </button>
        <ConversationConfig editItem={editIdItem} />
      </dialog>
    </>
  );
}
