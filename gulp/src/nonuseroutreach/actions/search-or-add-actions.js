import {createAction} from 'redux-actions';
import {errorAction} from '../../common/actions/error-actions';

/**
 * We have a new search field or we are starting over.
 *
 *  instance: search instance to work with
 */
export const resetSearchOrAddAction = createAction('SEARCH_RESET',
  instance => ({instance}));

/**
 * The user updated the search field.
 *
 * This action is not expected to be debounced.
 *
 *  instance: search instance to work with
 *  searchString: is the text of the current search string
 */
export const searchUpdateAction = createAction('SEARCH_UPDATE',
  (instance, searchString) => ({instance, searchString}));

/**
 * The search text settled down.
 *
 *  instance: search instance to work with
 *  loadingId: an id used to associate receipt of search results.
 *    Later, if search results from an earlier (stale) settle action arrive
 *    they will be ignored. The id should be unique within the lifetime of this
 *    reducer state chain.
 */
export const searchSettledAction = createAction('SEARCH_SETTLED',
  (instance, loadingId) => ({instance, loadingId}));

/**
 * Search results have been received.
 *
 *  instance: search instance to work with
 *  results: a list of search results [
 *    {value: ..., display: ''}
 *  ]
 *  loadingId: the id established by an earlier searchSettledAction.
 */
export const searchResultsReceivedAction =
  createAction('SEARCH_RESULTS_RECEIVED',
    (instance, results, loadingId) => ({instance, results, loadingId}));

/**
 * The user selected a previous search result.
 *
 *  instance: search instance to work with
 *  selected: a single item in the form of a search result.
 *    {value: ..., display: ''}
 */
export const searchResultSelectedAction =
  createAction('SEARCH_RESULT_SELECTED',
    (instance, selected) => ({instance, selected}));

/**
 * The user moved their active item up or down.
 *
 *  instance: search instance to work with
 *  delta: number to add to the index. e.g. 1, or -1
 */
export const addToActiveIndexAction =
  createAction('SEARCH_RESULT_ADD_TO_ACTIVE_INDEX',
    (instance, delta) => ({instance, delta}));

/**
 * The user made a particular item active.
 *
 *  instance: search instance to work with
 *  delta: number to add to the index. e.g. 1, or -1
 */
export const setActiveIndexAction =
  createAction('SEARCH_RESULT_SET_ACTIVE_INDEX',
    (instance, index) => ({instance, index}));

/**
 * Run the search API with the current search.
 *
 * Use this when the search term settles down to actually run the search.
 *
 *  instance: search instance to work with
 *  extraParams: {key: value} additional parameters to pass to the api.
 *    i.e. {partner_id: '3'}
 */
export function doSearch(instance, extraParams) {
  return async (dispatch, getState, {idGen, api}) => {
    try {
      const {searchString} = getState().search[instance];
      const loadingId = idGen.nextId();
      dispatch(searchSettledAction(instance, loadingId));
      const results = await api.search(instance, searchString, extraParams);
      dispatch(searchResultsReceivedAction(instance, results, loadingId));
    } catch (e) {
      dispatch(errorAction(e.message));
    }
  };
}
