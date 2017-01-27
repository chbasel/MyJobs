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
 *  startMonth stores the current month for the calendar when the app boots
 *  startDay stores the current month for the calendar when the app boots
 *  startYear stores the current month for the calendar when the app boots
 *  endMonth stores the end month for the calendar when the app boots
 *  endDay stores the end day for the calendar when the app boots
 *  endYear stores the end year for the calendar when the app boots
 *  activeReport stores the current report type for sending back to the API
 *  primaryDimensions stores the primary dimensions given back from the API to create the sidebar list
 *  activePrimaryDimension stores the current primary dimension that is actively chosen at that time
 *  startDate and endDate are added to the tab object when the page is created. They are used to store the dates for sending off to the API when the call is made
 */

let navCount = 1;
export const initialPageData = {
  pageFetching: true,
  navFetching: false,
  messageShown: false,
  navigation: [],
  activeFilters: [],
  startMonth: '',
  startDay: '',
  startYear: '',
  endMonth: '',
  endDay: '',
  endYear: '',
  globalStartDate: '',
  globalEndDate: '',
  stateCustomRange: '',
  activeReport: '',
  primaryDimensions: {},
  activePrimaryDimension: '',
  deletedNavigation: [],
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
  'MARK_UPDATE_MESSAGE_SHOWN': (state, action) => {
    const messageShown = action.payload;
    return {
      ...state,
      messageShown: messageShown,
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
          crumbs: [loadData.pageData.column_names[0].label.toLowerCase()],
          activeFilters: [],
          PageLoadData: loadData.pageData,
        },
      ],
      globalStartDate: loadData.startDate,
      globalEndDate: loadData.endDate,
      stateCustomRange: loadData.loadRange,
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
    const navigation = state.navigation;
    const checkType = action.payload.type;
    const index = findIndex(state.activeFilters, f => f.type === checkType);
    let tabIndex;
    if (index > -1) {
      for (let i = 0; i < navigation.length; i++) {
        if (navigation[i].active) {
          tabIndex = i;
          break;
        } else {
          tabIndex = 0;
        }
      }
      return {
        ...state,
        navigation: state.navigation.slice(0, tabIndex + 1),
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
          crumbs: filterData.crumbs,
          startDate: filterData.date.startDate,
          activeFilters: filterData.tabFilter,
          endDate: filterData.date.endDate,
          PageLoadData: filterData.data,
        },
      ],
      stateCustomRange: filterData.loadRange,
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
  'UPDATE_SWITCHED_TAB_DATA': (state, action) => {
    const updatedTabData = action.payload;
    return {
      ...state,
      navigation: state.navigation.map(nav => {
        if (nav.active) {
          return {
            ...nav,
            startDate: updatedTabData.date.startDate,
            endDate: updatedTabData.date.endDate,
            PageLoadData: updatedTabData.data,
          };
        }
        return nav;
      }),
    };
  },
  'BREADCRUMB_SWITCH_TAB': (state, action) => {
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
  'RESTORE_DELETED_TAB': (state, action) => {
    const replacedTab = action.payload;
    const newNavigation = state.navigation.slice(0);
    newNavigation.splice(replacedTab.index, 0, replacedTab.deleted);
    return {
      ...state,
      navigation: newNavigation,
    };
  },
  'DELETE_STORED_DELETED_TAB': (state, action) => {
    const deleteStored = action.payload;
    return {
      ...state,
      deletedNavigation: state.deletedNavigation.filter((deleted) => {
        return deleted.navId !== deleteStored.navId;
      }),
    };
  },
  'SET_CURRENT_RANGE': (state, action) => {
    const range = action.payload;
    return {
      ...state,
      stateCustomRange: range,
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
          crumbs: [mainDimensionData.pageData.column_names[0].label.toLowerCase()],
          startDate: mainDimensionData.startDate,
          endDate: mainDimensionData.endDate,
          PageLoadData: mainDimensionData.pageData,
          currentDateRange: mainDimensionData.loadRange,
        },
      ],
      globalStartDate: mainDimensionData.startDate,
      globalEndDate: mainDimensionData.endDate,
      activeFilters: [],
      stateCustomRange: mainDimensionData.loadRange,
    };
  },
  'SET_MAIN_DIMENSION': (state, action) => {
    const activeMainDimension = action.payload;
    return {
      ...state,
      activePrimaryDimension: activeMainDimension,
    };
  },
  'STORE_DELETED_TAB': (state, action) => {
    const deletedData = action.payload;
    return {
      ...state,
      deletedNavigation: state.deletedNavigation.filter(deleted => deleted.PageLoadData.group_by !== deletedData.PageLoadData.group_by).concat(deletedData),
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
  'SET_CURRENT_START_MONTH': (state, action) => {
    const currentMonth = action.payload;
    return {
      ...state,
      startMonth: currentMonth,
    };
  },
  'SET_CURRENT_START_YEAR': (state, action) => {
    const currentYear = action.payload;
    return {
      ...state,
      startYear: currentYear,
    };
  },
  'SET_CURRENT_START_DAY': (state, action) => {
    const currentDay = action.payload;
    return {
      ...state,
      startDay: currentDay,
    };
  },
  'SET_CURRENT_END_MONTH': (state, action) => {
    const currentMonth = action.payload;
    return {
      ...state,
      endMonth: currentMonth,
    };
  },
  'SET_CURRENT_END_YEAR': (state, action) => {
    const currentYear = action.payload;
    return {
      ...state,
      endYear: currentYear,
    };
  },
  'SET_CURRENT_END_DAY': (state, action) => {
    const currentDay = action.payload;
    return {
      ...state,
      endDay: currentDay,
    };
  },
  'SET_SELECTED_END_MONTH': (state, action) => {
    const selectedMonth = action.payload;
    return {
      ...state,
      endMonth: selectedMonth,
    };
  },
  'SET_SELECTED_END_YEAR': (state, action) => {
    const selectedYear = action.payload;
    return {
      ...state,
      endYear: selectedYear,
    };
  },
  'SET_SELECTED_END_DAY': (state, action) => {
    const selectedDay = action.payload;
    return {
      ...state,
      endDay: selectedDay,
    };
  },
  'SET_SELECTED_START_MONTH': (state, action) => {
    const selectedMonth = action.payload;
    return {
      ...state,
      startMonth: selectedMonth,
    };
  },
  'SET_SELECTED_START_YEAR': (state, action) => {
    const selectedYear = action.payload;
    return {
      ...state,
      startYear: selectedYear,
    };
  },
  'SET_SELECTED_START_DAY': (state, action) => {
    const selectedDay = action.payload;
    return {
      ...state,
      startDay: selectedDay,
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
            currentDateRange: selectedRangeData.loadRange,
          };
        }
        return nav;
      }),
      globalStartDate: selectedRangeData.startDate,
      globalEndDate: selectedRangeData.endDate,
      stateCustomRange: selectedRangeData.loadRange,
    };
  },
  'SET_CUSTOM_RANGE': (state, action) => {
    const customRangeData = action.payload;
    return {
      ...state,
      navigation: state.navigation.map((nav) => {
        if (nav.active === true) {
          return {
            ...nav,
            startDate: customRangeData.startDate,
            endDate: customRangeData.endDate,
            PageLoadData: customRangeData.data,
            currentDateRange: customRangeData.loadRange,
          };
        }
        return nav;
      }),
      globalStartDate: customRangeData.startDate,
      globalEndDate: customRangeData.endDate,
      stateCustomRange: customRangeData.loadRange,
    };
  },
}, initialPageData);
