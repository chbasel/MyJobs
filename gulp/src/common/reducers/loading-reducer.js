import {handleActions} from 'redux-actions';

export const initialLoading = {
  mainPage: true,
  fields: {},
  other: {},
};


/**
 * format for loading indicators
 *
 * A loading indicator means that we are doing work in the background to gather
 * data which will be shown later. This gives the UI an opportunity to hide
 * incomplete or stale data from the user.
 *
 *  mainPage: controls loading state for the direct children of the routing
 *    parent of the app.
 *
 *  fields[field]: object of boolean values indicating loading state of various
 *    fields.
 *
 *  other[key]: object of boolean values indicating loading state of other
 *    arbitrary objects in the app.
 */
export default handleActions({
  'MARK_PAGE_LOADING': (state, action) => {
    const pageLoading = action.payload;
    return {
      ...state,
      mainPage: pageLoading,
    };
  },

  'MARK_FIELD_LOADING': (state, action) => {
    const {field, value} = action.payload;
    return {
      ...state,
      fields: {
        ...state.fields,
        [field]: value,
      },
    };
  },

  'MARK_OTHER_LOADING': (state, action) => {
    const {key, value} = action.payload;
    return {
      ...state,
      other: {
        ...state.other,
        [key]: value,
      },
    };
  },
}, initialLoading);
