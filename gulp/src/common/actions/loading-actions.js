import {createAction} from 'redux-actions';

/**
 * Marks the main "page" area as loading or not.
 *
 * payload is a boolean.
 */
export const markPageLoadingAction = createAction('MARK_PAGE_LOADING');

export const markNavLoadingAction = createAction('MARK_NAV_LOADING');


/**
 * Marks a field as loading or not.
 *
 * field: name of field on the screen which is loading
 * value: boolean
 */
export const markFieldLoadingAction = createAction(
  'MARK_FIELD_LOADING', (field, value) => ({field, value}));


/**
 * Marks an arbitrary key as loading
 *
 * key: unique key for arbitrary thing on the screen which is loading
 * value: boolean
 */
export const markOtherLoadingAction = createAction(
  'MARK_OTHER_LOADING', (key, value) => ({key, value}));
