import {handleActions} from 'redux-actions';

export default handleActions({
  /** payload: An object whose keys are app-level access names and values are
   *           activities.
   *  example:
   *   {
   *     PRM: [
   *       {
   *         id: 2,
   *         name: 'read role',
   *         description: 'View existing roles.'
   *       }
   *     ]
   *   }
   */
  'UPDATE_ACTIVITIES': (state, action) => {
    const result = {
      ...state,
      activities: action.payload,
    };
    return result;
  },
}, {
  activities: {},
});
