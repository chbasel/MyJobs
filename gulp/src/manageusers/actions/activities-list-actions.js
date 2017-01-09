import {createAction} from 'redux-actions';

export const updateActivitiesAction =
  createAction('UPDATE_ACTIVITIES');

import {errorAction} from '../../common/actions/error-actions';

/**
 * Asynchronously fetches an updated list of activities grouped by their
 * app-level accesss
 */
export function doRefreshActivities() {
  return async (dispatch, _, {api}) => {
    try {
      const results = await api.getActivities();
      dispatch(updateActivitiesAction(results));
    } catch (exc) {
      dispatch(errorAction(exc.message));
    }
  };
}
