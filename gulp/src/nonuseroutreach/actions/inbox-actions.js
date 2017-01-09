import {createAction} from 'redux-actions';
import {errorAction} from '../../common/actions/error-actions';

export const validateInboxAction = createAction('VALIDATE_INBOX');
export const saveInboxAction = createAction('SAVE_INBOX');
export const getInboxesAction = createAction('GET_INBOXES');
export const resetInboxAction = createAction('RESET_INBOX');
export const updateInboxAction = createAction('UPDATE_INBOX');
export const deleteInboxAction = createAction('DELETE_INBOX');

// Note: Each of the asynchronous calls will dispatch an `errorAction` if an
// exception was thrown.

/* doSaveInbox
 *
 * Given an unsaved :inbox: asynchronously creates an inbox based on that
 * inbox's :email: and dispatches `saveInboxAction`. Then asynchronously
 * fetches an updated list of inboxes and dispatches `getInboxesAction`.
 */
export function doSaveInbox(inbox) {
  return async (dispatch, _, {api}) => {
    try {
      const newInbox = await api.createNewInbox(inbox.email);
      dispatch(saveInboxAction(newInbox));

      const inboxes = await api.getExistingInboxes();
      dispatch(getInboxesAction(inboxes));
    } catch (exception) {
      dispatch(errorAction(exception.message));
    }
  };
}

/* doGetInboxes
 *
 * Asynchronously fetches an updated list of inboxes and dispatches
 * `getInboxesAction`.
 */
export function doGetInboxes() {
  return async (dispatch, _, {api}) => {
    try {
      const inboxes = await api.getExistingInboxes();
      dispatch(getInboxesAction(inboxes));
    } catch (exception) {
      dispatch(errorAction(exception.message));
    }
  };
}

/* doUpdateInbox
 *
 * Given a modified inbox, asynchronously updates an inbox based on that
 * inbox's :pk: and :email: and dispatches `updateInboxAction' if the
 * asynchronous update was a success.
 */
export function doUpdateInbox(inbox) {
  return async (dispatch, _, {api}) => {
    try {
      const response = await api.updateInbox(inbox.pk, inbox.email);
      if (response.status === 'success') {
        dispatch(updateInboxAction(inbox));
      } else {
        dispatch(errorAction(response.status));
      }
    } catch (exception) {
      dispatch(errorAction(exception.message));
    }
  };
}

/* doDeleteInbox
 * Given an unmodified inbox, asynchronously deletes that inbox based on that
 * inbox's :pk: and dispatches `deleteInboxAction` if the asynchronous delete
 * was a success.
 */
export function doDeleteInbox(inbox) {
  return async (dispatch, _, {api}) => {
    try {
      const response = await api.deleteInbox(inbox.pk);
      if (response.status === 'success') {
        dispatch(deleteInboxAction(inbox));

        const inboxes = await api.getExistingInboxes();
        dispatch(getInboxesAction(inboxes));
      } else {
        dispatch(errorAction(response.status));
      }
    } catch (exception) {
      dispatch(errorAction(exception.message));
    }
  };
}
