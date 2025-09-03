import { Input } from "@headlessui/react";
import dayjs from "dayjs";
import { useEffect, useMemo, useState } from "react";
import type { Conversation } from "../../../app/core/dashboard";
import { ConversationsTableItem } from "./ConversationsTableItem";

export const ConversationsTable = ({
  conversations,
}: {
  conversations?: Conversation[];
}) => {
  const dates = useMemo(() => {
    return (conversations ?? [])
      .map((item) => item.date_created)
      .sort((a, b) => (a > b ? 1 : -1));
  }, [conversations]);

  const minDate = useMemo(() => {
    return (dates[0] ?? "").substring(0, 10);
  }, [dates]);
  const maxDate = useMemo(() => {
    return (dates[dates.length - 1] ?? "").substring(0, 10);
  }, [dates]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (dates.length > 0) {
      setStartDate(dates[0].substring(0, 10));
      setEndDate(dates[dates.length - 1].substring(0, 10));
    }
  }, [dates]);

  const onDateRangeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.name === "range-start") {
      setStartDate(event.target.value);
    }
    if (event.target.name === "range-end") {
      setEndDate(event.target.value);
    }
  };

  const onSearchQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const filteredConversations = useMemo(() => {
    return conversations?.filter(
      (item) =>
        (startDate
          ? dayjs(item.date_created).isAfter(
              dayjs(startDate).subtract(1, "day"),
              "day",
            )
          : true) &&
        (endDate
          ? dayjs(item.date_created).isBefore(
              dayjs(endDate).add(1, "day"),
              "day",
            )
          : true) &&
        (searchQuery
          ? item.name.includes(searchQuery) ||
            item.description.includes(searchQuery)
          : true),
    );
  }, [startDate, endDate, searchQuery, conversations]);

  const hasConversations = useMemo(() => {
    return !!conversations && conversations?.length > 0;
  }, [conversations]);

  return (
    <div className="flex flex-col items-start h-full w-[85%] mx-auto py-10">
      <div id="heading" className="flex w-full justify-between flex-wrap">
        <div id="heading-text">
          <h1 className="text-5xl font-bold mb-8">Conversations</h1>
          <h2 className="mb-16">
            {hasConversations
              ? "Find all conversations created below."
              : "No conversation found. Create one by clicking the button on the right."}
          </h2>
        </div>
        <a
          className="mb-8 px-5 py-3 bg-secondary text-white rounded-md h-fit"
          href="/conversation/new"
        >
          + Create conversation
        </a>
      </div>
      {hasConversations && (
        <>
          <div
            id="conversation-filtering-control"
            className="filter-row flex bg-gray-50 p-4 rounded-xl my-2 gap-2 w-full justify-between items-center-safe flex-wrap"
          >
            <search className="h-min">
              <form className="h-min">
                <input
                  type="search"
                  id="conversation-query"
                  name="conversation"
                  placeholder="Search for Conversations"
                  className="bg-white rounded-md p-2 h-min shadow-md border-1 border-gray-200"
                  onInput={onSearchQueryChange}
                />
              </form>
            </search>
            {filteredConversations?.length !== conversations?.length && (
              <p>
                Showing {filteredConversations?.length} of{" "}
                {conversations?.length} conversations
              </p>
            )}

            <DateRangePicker
              minDate={minDate}
              maxDate={maxDate}
              startDate={startDate}
              endDate={endDate}
              onChange={onDateRangeChange}
            />
          </div>
          {filteredConversations && (
            <div className="border border-gray-200 rounded-2xl shadow-lg w-full min-w-min">
              <table
                id="conversation-table"
                className="w-full border-collapse min-w-3xl"
              >
                <thead>
                  <tr className="text-gray-500 bottom-2 border-b-gray-200 border-b items-center grid grid-cols-[3em_2.25fr_1fr_1fr_1fr_1fr_0.6fr]">
                    <th className="text-left p-5">
                      <Input type="checkbox" className="h-5 w-5" />
                    </th>
                    <th className="text-left p-5">Conversation Title</th>
                    <th className="text-left p-5">Number of Participants</th>
                    <th className="text-left p-5">Date Created</th>
                    <th className="text-left p-5">Status</th>
                    <th className="text-left p-5">Created By</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredConversations.map((conversation) => (
                    <ConversationsTableItem
                      conversation={conversation}
                      key={conversation.id}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
};

function DateRangePicker({
  minDate,
  maxDate,
  startDate,
  endDate,
  onChange,
}: {
  minDate?: string;
  maxDate?: string;
  startDate?: string;
  endDate?: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  const today = new Date();
  const todayFormatted = today.toISOString().substring(0, 10);
  const buttonName = useMemo(() => {
    if (!startDate && !endDate) {
      return "Date";
    }
    return `${startDate} - ${endDate}`;
  }, [startDate, endDate]);

  const onDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) onChange(event);
  };

  return (
    <details className="[&:open>summary]:rounded-br-none relative">
      <summary className="border-1 border-gray-200 shadow-md px-2 py-2 rounded-xl flex flex-row items-center gap-x-2 w-max cursor-pointer bg-white">
        {buttonName}
      </summary>
      <form className="flex flex-col border-1 border-gray-200 absolute bg-white p-4 rounded-b-xl rounded-tl-xl w-max right-0 flex flex-col gap-4 items-center">
        <input
          className="p-2 border-1 border-gray-200 rounded-md"
          type="date"
          id="start"
          name="range-start"
          value={startDate ?? todayFormatted}
          min={minDate}
          max={maxDate}
          onChange={onDateChange}
        />
        <p>to</p>
        <input
          className="p-2 border-1 border-gray-200 rounded-md"
          type="date"
          id="end"
          name="range-end"
          value={endDate ?? todayFormatted}
          min={minDate}
          max={maxDate}
          onChange={onDateChange}
        />
      </form>
    </details>
  );
}
