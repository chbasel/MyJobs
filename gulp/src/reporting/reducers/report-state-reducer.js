import {handleActions} from 'redux-actions';
import {map, filter as lodashFilter, contains} from 'lodash-compat/collection';
import {omit} from 'lodash-compat/object';
import {isEqual} from 'lodash-compat/lang';

const maxNameLength = 24;

function addOrReplaceByValues(original, items) {
  const removeValues = map(items, i => i.value);
  // Filter out the old thing, place the new one at the end.
  return [
    ...lodashFilter(original, i => !contains(removeValues, i.value)),
    ...items,
  ];
}

function replaceItemAtIndex(items, atIndex, newItem) {
  // Create a new array if the old one apparently didn't exist.
  if (!items) {
    return [newItem];
  }
  // If this is an unknown index, put the item at the end.
  if (!(atIndex in items)) {
    return [...items, newItem];
  }
  // Otherwise, replace the matching index.
  return map(items, (item, index) =>
    index === atIndex ? newItem : item);
}

export function withFilterDirtied(oldState, newState) {
  if (isEqual(oldState.currentFilter, newState.currentFilter)) {
    return newState;
  }
  return {
    ...newState,
    currentFilterDirty: true,
  };
}

/**
 * report filter state format: {
 *
 *  describes the controls present for selecting records for this report.
 *  filterInterface: [
 *    {
 *      filter: column filtered by this control; i.e. "contact"
 *      interfaceType: type of control to use; i.e. "date_range"
 *      display: display name for this control; i.e. "Contacts"
 *      isValid: whether or not the current report criteria is valid. For
 *      instance, in a communication record report, if no partners or contacts
 *      are returned, this would be false.
 *      TODO: add filterType to specify the type of filter data required
 *        i.e. "date_range", "or", "and_or", "string", etc.
 *    }
 *  ]
 *
 *  help[key] = boolean
 *    which controls have help available
 *    key: see filter in filterInterface
 *    boolean: true if help is available
 *
 *  hints[key] = [{value: filter value, display user sees this}]
 *    last loaded hints available to the user for a field
 *    key: which field this applies to
 *    value: what to show the user and what it represents
 *
 *  currentFilter[key] = filterData
 *    items selected by the user, with display data
 *    key: see filter in filterInterface
 *    filterData: varies according to interfaceType
 *      date_range: [datestring, datestring] where datestring is "MM/DD/YYYY"
 *      city_state:
 *      {city: string or null, state: string or null}
 *      search_multiselect:
 *        [{value: filter value, display: user sees this}]
 *      tags:
 *        [[{value: filter value, display: user sees, hexColor: "xxxxxx"}]]
 *
 *  reportName: name of the currently configured report
 *
 *  errors[key] = [messages]
 *    errors in this report configuration
 *    key: see filter in filterInterface or "$ALL" for errors associated with
 *      no particular field. 'reportName' is served for the reportName control.
 *    messages: a list of strings, intended to be shown as a bulleted list.
 *
 *  currentFilterDirty: boolean
 *    indicates that some change has been made to currentFilter.
 *    this can be reset to false. It will be set to true the next time
 *    currentFilter changes.
 * }
 */
export default handleActions({
  'START_NEW_REPORT': (state, action) => {
    const {
      defaultFilter: currentFilter,
      help,
      filters: filterInterface,
      name: reportName,
    } = action.payload;
    return {
      currentFilter,
      help,
      reportName,
      filterInterface,
      errors: {},
      hints: {},
      currentFilterDirty: false,
      isValid: true,
    };
  },

  'SET_SIMPLE_FILTER': (state, action) => {
    const {field, item} = action.payload;
    let newFilter;
    if (typeof item === 'undefined') {
      newFilter = omit(state.currentFilter, field);
    } else {
      newFilter = {
        ...state.currentFilter,
        [field]: item,
      };
    }

    return withFilterDirtied(state, {
      ...state,
      currentFilter: newFilter,
    });
  },

  'ADD_TO_OR_FILTER': (state, action) => {
    const {field, items} = action.payload;
    const {currentFilter} = state;

    const orFilter = currentFilter[field] || [];
    const newOrFilter = addOrReplaceByValues(orFilter, items);
    return withFilterDirtied(state, {
      ...state,
      currentFilter: {
        ...state.currentFilter,
        [field]: newOrFilter,
      },
    });
  },

  'REMOVE_FROM_OR_FILTER': (state, action) => {
    const {field, items} = action.payload;
    const {currentFilter} = state;

    if (!currentFilter.hasOwnProperty(field)) {
      return state;
    }
    const orFilter = currentFilter[field];
    const removeValues = map(items, i => i.value);
    const newOrFilter = lodashFilter(orFilter,
      i => !contains(removeValues, i.value));

    const newFilter = {
      ...currentFilter,
      [field]: newOrFilter,
    };

    return withFilterDirtied(state, {
      ...state,
      currentFilter: newFilter,
    });
  },

  'ADD_TO_AND_OR_FILTER': (state, action) => {
    const {field, index, items} = action.payload;
    const {currentFilter} = state;

    const newFilter = replaceItemAtIndex(
      currentFilter[field],
      index,
      addOrReplaceByValues(
        (state.currentFilter[field] || [])[index],
        items));

    return withFilterDirtied(state, {
      ...state,
      currentFilter: {
        ...currentFilter,
        [field]: newFilter,
      },
    });
  },

  'REMOVE_FROM_AND_OR_FILTER': (state, action) => {
    const {field, index, items} = action.payload;
    const {currentFilter} = state;

    const currentRow = (currentFilter[field] || [])[index] || [];

    if (!(index in currentFilter[field])) {
      return state;
    }

    const removeValues = map(items, i => i.value);
    const newRow = lodashFilter(currentRow,
      i => !contains(removeValues, i.value));

    let andGroup;
    if (newRow.length < 1) {
      andGroup = lodashFilter(currentFilter[field], (_, i) => i !== index);
    } else {
      andGroup = replaceItemAtIndex(
        state.currentFilter[field],
        index,
        newRow);
    }

    // If the group is empty, return the filter without this key.
    const newFilter = {
      ...currentFilter,
      [field]: andGroup,
    };

    return withFilterDirtied(state, {
      ...state,
      currentFilter: newFilter,
    });
  },

  'EMPTY_FILTER': (state, action) => {
    const {field} = action.payload;
    return {
      ...state,
      currentFilterDirty: true,
      currentFilter: {
        ...state.currentFilter,
        [field]: [],
      },
    };
  },

  'UNLINK_FILTER': (state, action) => {
    const {field} = action.payload;
    return {
      ...state,
      currentFilterDirty: true,
      currentFilter: {
        ...state.currentFilter,
        [field]: {nolink: true},
      },
    };
  },

  'DELETE_FILTER': (state, action) => {
    const {field} = action.payload;
    return {
      ...state,
      currentFilterDirty: true,
      currentFilter: {
        ...omit(state.currentFilter, field),
      },
    };
  },

  'SET_REPORT_NAME': (state, action) => {
    const reportName = action.payload;
    const cappedReportName = reportName.substring(0, maxNameLength);
    return {...state, reportName: cappedReportName};
  },

  'RECEIVE_HINTS': (state, action) => {
    const {field, hints} = action.payload;
    return {
      ...state,
      hints: {
        ...state.hints,
        [field]: hints,
      },
    };
  },

  'CLEAR_HINTS': (state, action) => {
    const field = action.payload;
    return {
      ...state,
      hints: omit(state.hints, (_, k) => k === field),
    };
  },

  'RESET_CURRENT_FILTER_DIRTY': (state) => {
    return {
      ...state,
      currentFilterDirty: false,
    };
  },

  'SET_VALID': (state, action) => ({...state, isValid: action.payload}),

  'UPDATE_RECORD_COUNT': (state, action) => {
    const recordCount = action.payload;

    return {
      ...state,
      recordCount,
    };
  },
}, {
  currentFilter: {},
  filterInterface: [],
  reportName: '',
  hints: {},
  isValid: true,
});
