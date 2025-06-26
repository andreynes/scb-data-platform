import { format, isValid, parseISO } from 'date-fns';

/**
 * Форматирует дату в стандартную строку 'dd.MM.yyyy'.
 * Безопасно обрабатывает null, undefined и невалидные даты.
 * @param date - Объект Date, строка (предпочтительно ISO 8601) или число (timestamp).
 * @returns Отформатированная строка или '-' в случае ошибки.
 */
export function formatDate(date: Date | string | number | null | undefined): string {
  if (!date) {
    return '-';
  }

  const dateObj = typeof date === 'string' ? parseISO(date) : new Date(date);

  if (!isValid(dateObj)) {
    return '-'; // или можно вернуть String(date), чтобы увидеть исходное значение
  }

  return format(dateObj, 'dd.MM.yyyy');
}