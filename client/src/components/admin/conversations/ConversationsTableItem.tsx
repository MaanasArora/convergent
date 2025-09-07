import { Input } from '@headlessui/react';
import dayjs from 'dayjs';
import type { Conversation } from '../../../app/core/dashboard';
import { StatusPill } from '../../ui/StatusPill';

export const ConversationsTableItem = ({
  conversation,
}: {
  conversation: Conversation;
}) => {
  const editLink = `/conversation/${conversation.id}/edit`;

  return (
    <tr className='items-center grid grid-cols-[3em_2.25fr_1fr_1fr_1fr_1fr_0.6fr]'>
      <td className='p-5'>
        <Input type='checkbox' className='h-5 w-5' />
      </td>
      <td className='p-5'>
        <strong>{conversation.name}</strong>
        <br />
        {conversation.description}
      </td>
      <td className='p-5'>{conversation.num_participants}</td>
      <td className='p-5'>
        {dayjs(conversation.date_created).format('MMM D, YYYY')}
      </td>
      <td className='p-5'>
        <StatusPill isActive={conversation.is_active} />
      </td>
      <td className='p-5'>
        <span className='text-gray-600'>{conversation.author.username}</span>
      </td>
      <td className='p-5'>
        <div className='flex gap-4'>
          <a
            href={editLink}
            className='text-primary hover:underline'
            aria-label={`View ${conversation.name}`}>
            View
          </a>
        </div>
      </td>
    </tr>
  );
};
