import en from '@/messages/en.json';
import fr from '@/messages/fr.json';
import { Locale } from './config';

const messages: Record<Locale, Record<string, string>> = { en, fr };

export function getMessages(locale: Locale): Record<string, string> {
  return messages[locale] ?? messages.en;
}
