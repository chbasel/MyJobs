import {createAction} from 'redux-actions';
import {errorAction} from '../../common/actions/error-actions';

export const setErrorsAction = createAction('SET_ERRORS');
export const updateUsersAction = createAction('UPDATE_USERS');
export const updateRolesAction = createAction('UPDATE_ROLES');
export const validateEmailAction = createAction('VALIDATE_EMAIL');
export const addRolesAction = createAction('ADD_ROLES');
export const removeRolesAction = createAction('REMOVE_ROLES');
export const clearValidationAction = createAction('CLEAR_VALIDATION');
export const clearErrorsAction = createAction('CLEAR_ERRORS');
export const setCurrentUserAction = createAction('SET_CURRENT_USER');
export const setLastAdminAction = createAction('SET_LAST_ADMIN');

// Note: Each of the asynchronous calls will dispatch an `errorAction` if an
// exception was thrown.

/**
 * doRefreshUsers
 *
 * Asynchronously fetches an updated users object where keys are user ids and
 * values represent pertinent user information.
 */
export function doRefreshUsers() {
  return async (dispatch, _, {api}) => {
    try {
      const result = await api.getUsers();
      dispatch(updateUsersAction(result));
    } catch (exc) {
      dispatch(errorAction(exc.message));
    }
  };
}

/**
 * doRefreshRoles
 *
 * Asynchronously fetches an updated roles object where keys are role ids and
 * values represent pertinent role information.
 */
export function doRefreshRoles() {
  return async (dispatch, _, {api}) => {
    try {
      const result = await api.getAllRoles();
      dispatch(updateRolesAction(result));
    } catch (exc) {
      dispatch(errorAction(exc.message));
    }
  };
}

/**
 * doEditUser
 * Given a :userId:, array of roles :added:, and an array of roles :removed:,
 * asynchronously edit a user and refresh the app's array of users.
 */
export function doUpdateUserRoles(userId, added, removed) {
  return async (dispatch, _, {api}) => {
    try {
      const result = await api.updateUserRoles(userId, added, removed);
      const action = result.errors.length ? setErrorsAction : doRefreshUsers;
      dispatch(action(result.errors));
    } catch (exc) {
      dispatch(errorAction(exc.message));
    }
  };
}

/**
 * doAddUser
 * given an :email: address and an array of :roles:, associate a user with
 * the company.
 */
export function doAddUser(email, roles) {
  return async (dispatch, _, {api}) => {
    try {
      const result = await api.addUser(email, roles);
      const action = result.errors.length ? setErrorsAction : doRefreshUsers;
      // TODO: Do we want to notify the user of the exact changes?
      dispatch(action(result.errors));
    } catch (exc) {
      dispatch(errorAction(exc.message));
    }
  };
}

/**
 * doRemoveUser
 * Given a :userId: disassociate the user with a corresponding ID from the
 * current company
 */
export function doRemoveUser(userId) {
  return async (dispatch, _, {api}) => {
    try {
      const result = await api.removeUser(userId);
      const action = result.errors.length ? setErrorsAction : doRefreshUsers;
      dispatch(action(result.errors));
    } catch (exc) {
      dispatch(errorAction(exc.message));
    }
  };
}
