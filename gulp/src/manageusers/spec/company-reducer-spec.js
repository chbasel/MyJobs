import companyReducer, {
  initialCompany,
  initialValidation,
} from '../reducers/company-reducer';
import {
  setErrorsAction,
  updateUsersAction,
  updateRolesAction,
  validateEmailAction,
  addRolesAction,
  removeRolesAction,
  clearValidationAction,
  clearErrorsAction,
  setCurrentUserAction,
  setLastAdminAction,
} from '../actions/company-actions';

const dispatch = action => companyReducer(initialCompany, action);

describe('companyReducer', () => {
  describe('setErrorsAction', () => {
    it('should add a list of error messages to the app state', () => {
      const errors = [
        'first error',
        'second error',
      ];
      const result = dispatch(setErrorsAction(errors));

      expect(result.errors).toEqual(errors);
    });
  });

  describe('updateUsersAction', () => {
    it('should update the users object', () => {
      const users = {
        1: {
          roles: [
            'PRM User',
          ],
          lastInvitation: '2012-07-13',
          email: 'user@de.org',
          isVerified: false,
        },
        11: {
          roles: [
            'Admin',
          ],
          lastInvitation: '',
          email: 'admin@de.org',
          isVerified: true,
        }
      };

      const result = dispatch(updateUsersAction(users));
      expect(result.users).toEqual(users);
    });
  });

  describe('updateRolesAction', () => {
    it('should update the roles object', () => {
      const roles = {
        Admin: {
          activities: [
            {
              appAccess: 'PRM',
              name: 'create contact',
              description: 'Add new contacts.'
            },
            {
              appAccess: 'User Management',
              name: 'create user',
              description: 'Add new users.'
            },
          ],
        },
        'PRM User': {
          activities: [
            {
              appAccess: 'PRM',
              name: 'read contact',
              description: 'view existing contacts.'
            },
          ],
        }
      };
      const result = dispatch(updateRolesAction(roles));
      expect(result.roles).toEqual(roles);
    });
  });

  describe('validateEmailAction', () => {
    it('should permit valid email addresses', () => {
      const result = dispatch(validateEmailAction('foo@bar.com'));
      expect(result.validation.email.value).toEqual('foo@bar.com');
      expect(result.validation.email.errors).toEqual([]);
    });

    it('should not permit invalid email addresses', () => {
      const result = dispatch(validateEmailAction('asdjasdf3e'));
      expect(result.validation.email.value).toEqual('asdjasdf3e');
      expect(result.validation.email.errors).toEqual([
        'Invalid email address'
      ]);
    });
  });

  describe('addRolesAction', () => {
    it('should add specified roles to existing roles', () => {
      const state = {
        ...initialCompany,
        currentUser: 1,
        company: {
          ...initialCompany.company,
          users: {
            1: {
              roles: [
                'PRM User',
              ],
              lastInvitation: '2012-07-13',
              email: 'user@de.org',
              isVerified: false,
            },
          },
        }, 
        validation: {
          roles: {
            value: ['PRM User'],
          },
        },
      };

      const result = companyReducer(state, addRolesAction(['Admin']));
      expect(result.validation.roles.value).toEqual([
        'Admin',
        'PRM User',
      ]);
    });
  });

  describe('removeRolesAction', () => {
    it('should remove specified roles from existing roles', () => {
      const state = {
        ...initialCompany,
        currentUser: 1,
        company: {
          ...initialCompany.company,
          users: {
            1: {
              roles: [
                'PRM User',
                'Admin',
              ],
              lastInvitation: '2012-07-13',
              email: 'user@de.org',
              isVerified: false,
            },
          },
        }, 
        validation: {
          roles: {
            value: ['PRM User', 'Admin'],
          },
        },
      };
      const result = companyReducer(state, removeRolesAction(['PRM User']));

      expect(result.validation.roles.value).toEqual([
        'Admin',
      ]);
    });
  });

  describe('clearValidationAction', () => {
    it('should reset the validation state', () => {
      const state = {
        ...initialCompany,
        validation: {
          ...initialCompany.validation,
          email: {
            value: 'asdfsadf',
            errors: ['Invalid email address'],
          }
        }
      };
      const result = companyReducer(state, clearValidationAction());

      expect(result.validation).toEqual(initialValidation);
    });
  });

  describe('clearErrorsAction', () => {
    it('should clear app-wide errors', () => {
      const state = {
        ...initialCompany,
        errors: ['Some app-wide error'],
      };
      const result = companyReducer(state, clearErrorsAction());
      expect(result.errors).toEqual([]);
    });
  });

  describe('setCurrentUserAction', () => {
    it('should set the ID of the user currently being edited', () => {
      const result = dispatch(setCurrentUserAction(2));
      expect(result.currentUser).toEqual(2);
    });
  });

  describe('setLastAdminAction', () => {
    it('should set a boolean to the passed value', () => {
      expect(dispatch(setLastAdminAction(true)).lastAdmin).toEqual(true);
      expect(dispatch(setLastAdminAction(false)).lastAdmin).toEqual(false);
    });
  });
});
