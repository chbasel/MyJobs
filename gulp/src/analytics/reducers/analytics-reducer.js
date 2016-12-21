import {handleActions} from 'redux-actions';
import {findIndex} from 'lodash-compat';

/**
 *  Contents used for the entire app at this point. All state is currently held here
 *
 *  navCount starts the count of the tabs and increments as they are added
 *  pageFetching is used to show loading when the app initial boots
 *  navFetching is used when there is a new tab being created through filtering or dimension switching
 *  navigation holds the tabs and their independent data
 *  activeFilters stores the current filters for sending back to the API
 *  month stores the current month for when the app boots
 *  day stores the current month for when the app boots
 *  year stores the current month for when the app boots
 *  activeReport stores the current report type for sending back to the API
 *  primaryDimensions stores the primary dimensions given back from the API to create the sidebar list
 *  activePrimaryDimension stores the current primary dimension that is actively chosen at that time
 *  startDate and endDate are added to the tab object when the page is created. They are used to store the dates for sending off to the API when the call is made
 */

let navCount = 1;
export const initialPageData = {
  pageFetching: true,
  navFetching: false,
  navigation: [],
  activeFilters: [],
  month: '',
  day: '',
  year: '',
  activeReport: '',
  primaryDimensions: {},
  activePrimaryDimension: '',
};

export default handleActions({
  'MARK_PAGE_LOADING': (state, action) => {
    const pageLoad = action.payload;
    return {
      ...state,
      pageFetching: pageLoad,
    };
  },
  'MARK_NAV_LOADING': (state, action) => {
    const navLoad = action.payload;
    return {
      ...state,
      navFetching: navLoad,
    };
  },
  'SET_PAGE_DATA': (state, action) => {
    const loadData = action.payload;
    return {
      ...state,
      navigation: [
        ...state.navigation,
        {
          navId: navCount++,
          active: true,
          startDate: loadData.startDate,
          endDate: loadData.endDate,
          PageLoadData: loadData.pageData,
        },
      ],
    };
  },
  'SET_PRIMARY_DIMENSIONS': (state, action) => {
    return {
      ...state,
      activePrimaryDimension: action.payload.reports[0].value,
      primaryDimensions: {
        dimensionList: action.payload,
      },
    };
  },
  'STORE_INITIAL_REPORT': (state, action) => {
    return {
      ...state,
      activeReport: action.payload,
    };
  },
  'STORE_ACTIVE_FILTER': (state, action) => {
    const checkType = action.payload.type;
    const index = findIndex(state.activeFilters, f => f.type === checkType);
    if (index > -1) {
      return {
        ...state,
        navigation: state.navigation.slice(0, index + 1),
        activeFilters: state.activeFilters.slice(0, index).concat(action.payload),
      };
    }
    return {
      ...state,
      activeFilters: [
        ...state.activeFilters,
        action.payload,
      ],
    };
  },
  'STORE_ACTIVE_REPORT': (state, action) => {
    return {
      ...state,
      activeReport: action.payload,
    };
  },
  'SET_SELECTED_FILTER_DATA': (state, action) => {
    const filterData = action.payload;
    return {
      ...state,
      navigation: [
        ...state.navigation.map(nav => Object.assign({}, nav, {active: false})),
        {
          navId: navCount++,
          active: true,
          startDate: filterData.date.startDate,
          endDate: filterData.date.endDate,
          PageLoadData: filterData.data,
        },
      ],
    };
  },
  'SWITCH_ACTIVE_TAB': (state, action) => {
    const activeTab = action.payload;
    return {
      ...state,
      navigation: state.navigation.map((nav) => {
        if (nav.navId === activeTab) {
          return {
            ...nav,
            active: true,
          };
        }
        return {
          ...nav,
          active: false,
        };
      }),
    };
  },
  'SWITCH_MAIN_DIMENSION': (state, action) => {
    const mainDimensionData = action.payload;
    return {
      ...state,
      navigation: [
        {
          navId: navCount++,
          active: true,
          startDate: mainDimensionData.startDate,
          endDate: mainDimensionData.endDate,
          PageLoadData: mainDimensionData.pageData,
        },
      ],
      activeFilters: [],
    };
  },
  'SET_MAIN_DIMENSION': (state, action) => {
    const activeMainDimension = action.payload;
    return {
      ...state,
      activePrimaryDimension: activeMainDimension,
    };
  },
  'REMOVE_SELECTED_TAB': (state, action) => {
    const selectedTab = action.payload;
    return {
      ...state,
      navigation: state.navigation.filter((nav) => {
        if (state.navigation.length > 1) {
          return nav.navId !== selectedTab;
        }
        return nav;
      }),
    };
  },
  'SET_CURRENT_MONTH': (state, action) => {
    const currentMonth = action.payload;
    return {
      ...state,
      month: currentMonth,
    };
  },
  'SET_CURRENT_YEAR': (state, action) => {
    const currentYear = action.payload;
    return {
      ...state,
      year: currentYear,
    };
  },
  'SET_CURRENT_DAY': (state, action) => {
    const currentDay = action.payload;
    return {
      ...state,
      day: currentDay,
    };
  },
  'SET_SELECTED_MONTH': (state, action) => {
    const selectedMonth = action.payload;
    return {
      ...state,
      month: selectedMonth,
    };
  },
  'SET_SELECTED_YEAR': (state, action) => {
    const selectedYear = action.payload;
    return {
      ...state,
      year: selectedYear,
    };
  },
  'SET_SELECTED_DAY': (state, action) => {
    const selectedDay = action.payload;
    return {
      ...state,
      day: selectedDay,
    };
  },
  'SET_SELECTED_RANGE': (state, action) => {
    const selectedRangeData = action.payload;
    return {
      ...state,
      navigation: state.navigation.map((nav) => {
        if (nav.active === true) {
          return {
            ...nav,
            startDate: selectedRangeData.startDate,
            endDate: selectedRangeData.endDate,
            PageLoadData: selectedRangeData.data,
          };
        }
        return nav;
      }),
    };
  },
}, initialPageData);
