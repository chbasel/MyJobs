import {handleActions} from 'redux-actions';

const defaultState = {};

/**
 * several independent instances of this state can exist sot the whole state
 * is wrapped up in an object and actions all have instance parameters.
 *
 *
 *  format for search-or-add controls state {
 *    instance: {
 *      state: A test string indicating the phase of interaction we are in.
 *        'RESET': no interaction has occurred yet.
 *        'PRELOADING': the user has typed but we are waiting for input to
 *          settle down before making api calls.
 *        'LOADING': we are making api calls
 *        'RECEIVED': api results have been received
 *        'SELECTED': the user picked something
 *
 *      searchString: text which should appear in the control
 *      results: a list of received search results.
 *        [ {value: ..., display: 'string'} ]
 *      selected: an item from previous results which has been selected
 *        {value: ..., display: 'string'}
 *      loadingId: an unique value used to avoid mishandling receipt of out of
 *        order search results
 *    }
 *  }
 */
export default handleActions({
  'SEARCH_RESET': (state, action) => {
    const {instance} = action.payload;
    return {
      ...state,
      [instance]: {state: 'RESET'},
    };
  },

  'SEARCH_UPDATE': (state, action) => {
    const {instance, searchString} = action.payload;
    return {
      ...state,
      [instance]: {
        ...state[instance],
        state: 'PRELOADING',
        searchString,
      },
    };
  },

  'SEARCH_SETTLED': (state, action) => {
    const {instance, loadingId} = action.payload;

    return {
      ...state,
      [instance]: {
        ...state[instance],
        loadingId,
        state: 'LOADING',
      },
    };
  },

  'SEARCH_RESULTS_RECEIVED': (state, action) => {
    const {instance, results, loadingId} = action.payload;
    const expectedLoadingId = state[instance].loadingId;

    // If the loading id's don't match then these results are from an earlier
    // (stale) search which arrived after another search began. Ignore them.
    if (loadingId === expectedLoadingId) {
      return {
        ...state,
        [instance]: {
          ...state[instance],
          state: 'RECEIVED',
          results,
          activeIndex: 0,
        },
      };
    }

    return state;
  },

  'SEARCH_RESULT_SELECTED': (state, action) => {
    const {instance, selected} = action.payload;

    return {
      ...state,
      [instance]: {
        ...state[instance],
        state: 'SELECTED',
        selected,
      },
    };
  },

  'SEARCH_RESULT_ADD_TO_ACTIVE_INDEX': (state, action) => {
    const {instance, delta} = action.payload;
    const {results} = state[instance];

    // Disable active index if results are gone.
    if (!results || !results.length) {
      return {
        ...state,
        [instance]: {
          activeIndex: null,
        },
      };
    }

    const prevIndex = state[instance].activeIndex;
    if (!prevIndex && prevIndex !== 0) {
      return {
        ...state,
        [instance]: {
          ...state[instance],
          activeIndex: 0,
        },
      };
    }

    let newIndex = prevIndex + delta || 0;
    if (newIndex < 0) {
      newIndex = 0;
    }
    if (newIndex >= results.length) {
      newIndex = results.length - 1;
    }

    return {
      ...state,
      [instance]: {
        ...state[instance],
        activeIndex: newIndex,
      },
    };
  },

  'SEARCH_RESULT_SET_ACTIVE_INDEX': (state, action) => {
    const {instance, index} = action.payload;
    const {results} = state[instance];

    // Disable active index if results are gone.
    if (!results || !results.length) {
      return {
        ...state,
        [instance]: {
          activeIndex: null,
        },
      };
    }

    let newIndex = index;
    if (newIndex < 0) {
      newIndex = 0;
    }
    if (newIndex >= results.length) {
      newIndex = results.length - 1;
    }

    return {
      ...state,
      [instance]: {
        ...state[instance],
        activeIndex: newIndex,
      },
    };
  },
}, defaultState);
