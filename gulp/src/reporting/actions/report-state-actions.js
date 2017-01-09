import {createAction} from 'redux-actions';

/**
 * User wants to start a new report.
 *
 * payload is an object shaped like {
 *   defaultFilter: start of currentFilter
 *   help: see report-action-reducer
 *   filters: see report-action-reducer
 *   name: starting name for this report
 * }
 */
export const startNewReportAction = createAction('START_NEW_REPORT');

/**
 * User set a value in a filter that is a simple value assignment.
 *
 * field: which filter field to operate on.
 * item: filter value
 */
export const setSimpleFilterAction =
  createAction(
    'SET_SIMPLE_FILTER',
    (field, item) => ({field, item}));

/**
 * User added a value to an or filter.
 *
 * field: which filter field to operate on.
 * items: [filter values to add]
 */
export const addToOrFilterAction =
  createAction(
    'ADD_TO_OR_FILTER',
    (field, items) => ({field, items}));

/**
 * User removed a value from an or filter.
 *
 * field: which filter field to operate on.
 * items: [filter values to remove]
 */
export const removeFromOrFilterAction =
  createAction(
    'REMOVE_FROM_OR_FILTER',
    (field, items) => ({field, items}));

/**
 * User added a value to an and/or filter.
 *
 * field: which filter field to operate on.
 * index: which row of this field to operate on.
 * items: [filter values to add]
 */
export const addToAndOrFilterAction =
  createAction(
    'ADD_TO_AND_OR_FILTER',
    (field, index, items) => ({field, index, items}));

/**
 * User removed a value from an and/or filter.
 *
 * field: which filter field to operate on.
 * index: which row of this field to operate on.
 * items: [filter values to remove]
 */
export const removeFromAndOrFilterAction =
  createAction(
    'REMOVE_FROM_AND_OR_FILTER',
    (field, index, items) => ({field, index, items}));

/**
 * User set a date range filter.
 *
 * field: which filter field to operate on.
 * item: filter value: [begin date, end date] both 'MM/DD/YYYY'
 */
export const addToDateRangeFilterAction = setSimpleFilterAction;

/**
 * User changed the name of the report.
 *
 * payload is the new report name
 */
export const setReportNameAction = createAction('SET_REPORT_NAME');

/**
 * Api returned new hints.
 *
 * field: which filter field to operate on.
 * hints: may vary by filter type but is usually: [
 *   {value: some value, display: show to user, ...}
 * ]
 */
export const receiveHintsAction = createAction('RECEIVE_HINTS',
  (field, hints) => ({field, hints}));

/**
 * Need to clear all the known hints for a field.
 *
 * payload: string, which filter field to operate on.
 */
export const clearHintsAction = createAction('CLEAR_HINTS');

/**
 * We've cleaned whatever needed to react to filter changes.
 *
 * no payload
 */
export const resetCurrentFilterDirty =
  createAction('RESET_CURRENT_FILTER_DIRTY');

/**
 * Delete an "or" or "and/or" filter.
 *
 * field: which filter field to operate on.
 */
export const deleteFilterAction = createAction('DELETE_FILTER',
  (field) => ({field}));

/**
 * Empty an "or" or "and/or" filter.
 *
 * field: which filter field to operate on.
 */
export const emptyFilterAction = createAction('EMPTY_FILTER',
  (field) => ({field}));


/**
 * Mark a filter as unlinked. i.e. untagged
 *
 * field: which filter field to operate on.
 */
export const unlinkFilterAction = createAction('UNLINK_FILTER',
  (field) => ({field}));

/**
 * Mark the report as valid or invalid, which corresponds to an
 * enabled/disabled run button, respectively.
 *
 * payload: bool, whether or not the report is valid
 */
export const setValidAction = createAction('SET_VALID');

/**
 * Update the known record count for this report.
 *
 * payload: number, the new record count
 */
export const updateRecordCount = createAction('UPDATE_RECORD_COUNT');
