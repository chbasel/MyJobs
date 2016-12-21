import {difference, forOwn, union} from 'lodash-compat';
import {handleActions} from 'redux-actions';
import {validateEmail} from '../../common/email-validators';

// represents an unsaved user; each key represents a field on the user form
// along with the current value and associated errors
export const initialValidation = {
  email: {
    value: '',
    errors: [],
  },
  roles: {
    value: [],
    errors: [],
  },
};

export const initialCompany = {
  // TODO: move this to validation
  // the current user being edited
  currentUser: null,
  users: {},
  roles: {},
  // server-side errors
  errors: [],
  // TODO: rename onlyAdmin and move to validation?
  // whether or not the user being edited is the last admin for a company
  lastAdmin: false,
  // user-level field errors
  validation: initialValidation,
};

export default handleActions({
  /**
   * payload: array errors
   * state changes: :errors: is assigned the value of the payload
   */
  'SET_ERRORS': (state, action) => ({...state, errors: action.payload}),
  /**
   * payload: number
   * state changes: :currentUser: is assigned the value of the payload
   */
  'SET_CURRENT_USER': (state, action) => ({
    ...state,
    currentUser: action.payload,
  }),
  /**
   * payload: boolean
   * state changes: :lastAdmin is assigned the value of the payload
   */
  'SET_LAST_ADMIN': (state, action) => ({...state, lastAdmin: action.payload}),
  /**
   * payload: object keyed by user id
   * state changes: :users: is assigned the value of the payload.
   */
  'UPDATE_USERS': (state, action) => ({
    ...state,
    users: action.payload,
  }),
  /**
   * payload: object keyed by role name
   * state changes: :roles: is assigned the value of the payload.
   */
  'UPDATE_ROLES': (state, action) => ({
    ...state,
    roles: action.payload,
  }),
  /**
   * payload: undefined
   * state changes: :validation: is reset to :initialValidation:.
   */
  'CLEAR_VALIDATION': (state) => ({...state, validation: initialValidation}),
  /**
   * payload: undefined
   * state changes: :errors: is reset to an empty array.
   */
  'CLEAR_ERRORS': (state) => ({...state, errors: []}),
  /**
   * payload: email address
   * state changes: :validation.email: is updated with a value which
   * corresponds to the payload. If validation fails, its errors field will be
   * updated accordingly.
   */
  'VALIDATE_EMAIL': (state, action) => {
    const errors = validateEmail(action.payload) ? [] : [
      'Invalid email address',
    ];
    return {
      ...state,
      validation: {
        ...state.validation,
        email: {
          value: action.payload,
          errors: errors,
        },
      },
    };
  },
  /**
   * payload: an array of roles to add
   * state changes: :validation.roles: is updated with a value of the new
   * combined roles. If validation fails, its errors field will be updated
   * accordingly.
   */
  'ADD_ROLES': (state, action) => {
    const {validation, users, currentUser} = state;
    const newRoles = union(action.payload, validation.roles.value);
    const admins = {};

    forOwn(users, (value, key) => {
      const roles = key === currentUser ? newRoles : value.roles;
      if (roles.indexOf('Admin') > -1) {
        admins[key] = newRoles;
      }
    });
    const errors = [];
    if (!Object.keys(newRoles).length) {
      errors.push('A user must be assigned to at least one role.');
    }

    if (!Object.keys(admins).length) {
      errors.push('Each company must have at leat one user assigned to the ' +
                  'Admin role.');
    }

    return {
      ...state,
      validation: {
        ...validation,
        roles: {
          ...validation.roles,
          value: newRoles,
          errors: errors,
        },
      },
    };
  },
  /**
   * payload: an array of roles to remove
   * state changes: :validation.roles: is updated with a value of original
   * roles minuse those removed. if validation fails, its errors field will be
   * updated accordingly.
   */
  'REMOVE_ROLES': (state, action) => {
    const {validation, users, currentUser} = state;
    const newRoles = difference(validation.roles.value, action.payload);
    const admins = {};

    forOwn(users, (value, key) => {
      const roles = key === currentUser ? newRoles : value.roles;
      if (roles.indexOf('Admin') > -1) {
        admins[key] = roles;
      }
    });

    const errors = [];
    if (!Object.keys(newRoles).length) {
      errors.push('A user must be assigned to at least one role.');
    }

    if (!Object.keys(admins).length) {
      errors.push('Each company must have at least one user assigned to the ' +
                  'Admin role.');
    }

    return {
      ...state,
      validation: {
        ...validation,
        roles: {
          ...validation.roles,
          value: newRoles,
          errors: errors,
        },
      },
    };
  },
}, initialCompany);
