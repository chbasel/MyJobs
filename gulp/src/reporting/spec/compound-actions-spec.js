import {zip} from 'lodash-compat/array';
import {map, filter} from 'lodash-compat/collection';
import {
  setSimpleFilterAction,
  receiveHintsAction,
  clearHintsAction,
} from '../actions/report-state-actions';

import reportStateReducer from '../reducers/report-state-reducer';

import {
  startNewReportAction,
  updateRecordCount,
} from '../actions/report-state-actions';

import {
  startRunningReportAction,
  startRefreshingReportAction,
  removeRunningReportAction,
  replaceReportsListAction,
} from '../actions/report-list-actions';

import {
  replaceDataSetMenu,
} from '../actions/dataset-menu-actions';

import {
  doRunReport,
  doRefreshReport,
  doGetHelp,
  doInitialLoad,
  doLoadReportSetUp,
  doReportDataRedirect,
  doDataSetMenuFill,
  getFilterValuesOnly,
  runTrialReport,
  doUpdateFilterWithDependencies,
  doSetUpForClone,
} from '../actions/compound-actions';

import {
  markPageLoadingAction,
  markFieldLoadingAction,
  markOtherLoadingAction,
} from '../../common/actions/loading-actions';

import {
  errorAction,
  clearErrorsAction,
} from '../../common/actions/error-actions';

import {promiseTest} from '../../common/spec';
import IdGenerator from '../../common/id-generator';

import createReduxStore from '../../common/create-redux-store';
import {combineReducers} from 'redux';


// This improves messages on failed equality tests a bit.
const customMatchers = {
  toEqualActionList: function(util, customEqualityTesters) {
    return {
      compare: function(actual, expected) {
        const actualTypes = map(actual, r => r.type);
        const expectedTypes = map(expected, r => r.type);

        // Types match
        expect(actualTypes).toEqual(expectedTypes);

        // elements match
        for(const [a, e] of zip(actual, expected)) {
          expect(a).toEqual(e);
        };

        return {pass: true};
      },
    };
  },
}

class FakeApi {
  getSetUpMenuChoices() {}
  runReport() {}
  runTrialReport() {}
  refreshReport() {}
  listReports() {}
  getHelp() {}
  getFilters() {}
  getDefaultReportName() {}
  getReportInfo() {}
}


class FakeHistory {
  pushState() {}
  replaceState() {}
}


function spyOnSetUpMenuChoicesSuccess(api, reportDataId) {
  spyOn(api, 'getSetUpMenuChoices').and.returnValue(Promise.resolve({
    report_data_id: reportDataId,
    reporting_types: [{value: 'prm', display: 'PRM'}],
    report_types: [
      {value: 'partner', display: 'Partner'},
      {value: 'contact', display: 'Contacts'},
    ],
    data_types: [
      {value: 'unaggregated', display: 'Unaggregated'},
    ],
    selected_reporting_type: 'prm',
    selected_report_type: 'contact',
    selected_data_type: 'unaggregated',
  }));
}


describe('doInitialLoad', () => {
  let actions;
  let api;

  beforeEach(() => {
    actions = [];
    api = new FakeApi();
  });

  function dispatch(action) {
    actions.push(action);
  }

  function getState() {
    return {};
  }

  it('loads the report list', promiseTest(async () => {
    spyOn(api, 'listReports').and.returnValue(Promise.resolve([
      {id: 3, name: 'c', report_type: 3},
      {id: 4, name: 'd', report_type: 4},
    ]));
    await doInitialLoad()(dispatch, getState, {api});
    expect(actions).toEqual([
      replaceReportsListAction([
        {id: 3, name: 'c', report_type: 3},
        {id: 4, name: 'd', report_type: 4},
      ]),
    ]);
  }));
});


describe('doSetUpForClone', () => {
  let actions;
  let api;
  let history;

  beforeEach(() => {
    actions = [];
    api = new FakeApi();
    history = new FakeHistory();
  });

  function dispatch(action) {
    actions.push(action);
  }

  function getState() {
    return {};
  }

  it('handles the happy path', promiseTest(async () => {
    spyOn(api, 'getReportInfo').and.returnValue(Promise.resolve({
      report_data_id: 7,
      reporting_type: 'prm',
      report_type: 'contacts',
      data_type: 'unaggregated',
      name: 'thereportname',
      filter: {
        'locations': {city: 'Indy', state: 'IN'},
      }

    }));
    spyOn(history, 'pushState');

    await doSetUpForClone(history, 12)(dispatch, getState, {api});

    expect(api.getReportInfo).toHaveBeenCalledWith(12);
    expect(history.pushState).toHaveBeenCalledWith({
      name: 'Copy of thereportname',
      currentFilter: {
        'locations': {city: 'Indy', state: 'IN'},
      },
    }, '/set-up-report', {
      intention: 'prm',
      category: 'contacts',
      dataSet: 'unaggregated',
      reportDataId: 7,
    });
  }));

  it('handles arbitrary errors', promiseTest(async () => {
    spyOn(api, 'getReportInfo').and.throwError(new Error('Some Error'));
    await doSetUpForClone()(dispatch, getState, {api});
    expect(actions).toEqual([
      errorAction('Some Error'),
    ]);
  }));
});


describe('doReportDataRedirect', () => {
  let actions;
  let api;
  let history;

  beforeEach(() => {
    actions = [];
    api = new FakeApi();
    history = new FakeHistory();
    jasmine.addMatchers(customMatchers);
  });

  function dispatch(action) {
    actions.push(action);
  }

  function getState() {
    return {dataSetMenu: {}};
  }

  it('redirects to a default location', promiseTest(async () => {
    spyOnSetUpMenuChoicesSuccess(api, 7);
    spyOn(history, 'replaceState');
    await doReportDataRedirect(history)(dispatch, undefined, {api});
    expect(api.getSetUpMenuChoices).toHaveBeenCalledWith('', '', '');
    expect(history.replaceState).toHaveBeenCalledWith(null, '/set-up-report', {
      intention: 'prm',
      category: 'contact',
      dataSet: 'unaggregated',
      reportDataId: 7,
    });
    expect(actions).toEqualActionList([
      markPageLoadingAction(true),
      markOtherLoadingAction('dataSetMenu', true),
      replaceDataSetMenu({
        intentionChoices: [{value: 'prm', display: 'PRM'}],
        categoryChoices: [
          {value: 'partner', display: 'Partner'},
          {value: 'contact', display: 'Contacts'},
        ],
        dataSetChoices: [
          {value: 'unaggregated', display: 'Unaggregated'},
        ],
        intentionValue: 'prm',
        categoryValue: 'contact',
        dataSetValue: 'unaggregated',
        reportDataId: 7,
      }),
      markOtherLoadingAction('dataSetMenu', false),
    ]);
  }));

  it('uses choices with api', promiseTest(async () => {
    spyOnSetUpMenuChoicesSuccess(api, 8);
    spyOn(history, 'replaceState');
    await (
      doReportDataRedirect(history, 'a', 'b', 'c')
        (dispatch, undefined, {api}));
    expect(api.getSetUpMenuChoices).toHaveBeenCalledWith('a', 'b', 'c');
    expect(history.replaceState).toHaveBeenCalledWith(null, '/set-up-report', {
      intention: 'prm',
      category: 'contact',
      dataSet: 'unaggregated',
      reportDataId: 8,
    });
    expect(actions).toEqualActionList([
      markPageLoadingAction(true),
      markOtherLoadingAction('dataSetMenu', true),
      replaceDataSetMenu({
        intentionChoices: [{value: 'prm', display: 'PRM'}],
        categoryChoices: [
          {value: 'partner', display: 'Partner'},
          {value: 'contact', display: 'Contacts'},
        ],
        dataSetChoices: [
          {value: 'unaggregated', display: 'Unaggregated'},
        ],
        intentionValue: 'prm',
        categoryValue: 'contact',
        dataSetValue: 'unaggregated',
        reportDataId: 8,
      }),
      markOtherLoadingAction('dataSetMenu', false),
    ]);
  }));

  it('handles arbitrary errors', promiseTest(async () => {
    spyOn(api, 'getSetUpMenuChoices').and.throwError(new Error('Some error'));
    await doReportDataRedirect()(dispatch, getState, {api});
    expect(actions).toEqualActionList([
      markPageLoadingAction(true),
      markOtherLoadingAction('dataSetMenu', true),
      markOtherLoadingAction('dataSetMenu', false),
      markPageLoadingAction(false),
      errorAction("Some error"),
    ]);
  }));
});


describe('doDataSetMenuFill', () => {
  let actions;
  let api;
  let history;

  beforeEach(() => {
    actions = [];
    api = new FakeApi();
    history = new FakeHistory();
    jasmine.addMatchers(customMatchers);
  });

  function dispatch(action) {
    actions.push(action);
  }

  function getState() {
    return {dataSetMenu: {}};
  }

  it('skips calling setup menu if the choices match', promiseTest(async () => {
    function getState() {
      return {
        dataSetMenu: {
          intentionValue: 'prm',
          categoryValue: 'contact',
          dataSetValue: 'unaggregated',
          reportDataId: 7,
        },
      };
    }

    spyOnSetUpMenuChoicesSuccess(api, null);

    await doDataSetMenuFill('prm', 'contact', 'unaggregated')
      (dispatch, getState, {api});

    expect(api.getSetUpMenuChoices).not.toHaveBeenCalled();
    expect(actions).toEqual([]);
  }));

  it('makes an api call when needed', promiseTest(async () => {
    spyOnSetUpMenuChoicesSuccess(api, 8);

    await doDataSetMenuFill('prm', 'contact', 'unaggregated')
      (dispatch, getState, {api});

    expect(actions).toEqualActionList([
      markOtherLoadingAction('dataSetMenu', true),
      replaceDataSetMenu({
        intentionChoices: [{value: 'prm', display: 'PRM'}],
        categoryChoices: [
          {value: 'partner', display: 'Partner'},
          {value: 'contact', display: 'Contacts'},
        ],
        dataSetChoices: [
          {value: 'unaggregated', display: 'Unaggregated'},
        ],
        intentionValue: 'prm',
        categoryValue: 'contact',
        dataSetValue: 'unaggregated',
        reportDataId: 8,
      }),
      markOtherLoadingAction('dataSetMenu', false),
    ]);
  }));

  it('handles arbitrary errors', promiseTest(async () => {
    spyOn(api, 'getSetUpMenuChoices').and.throwError(new Error('Some error'));
    await doDataSetMenuFill()(dispatch, getState, {api});
    expect(actions).toEqualActionList([
      markOtherLoadingAction('dataSetMenu', true),
      markOtherLoadingAction('dataSetMenu', false),
      errorAction("Some error"),
    ]);
  }));
});


describe('doLoadReportSetUp', () => {
  let actions;
  let api;
  let history;

  beforeEach(() => {
    actions = [];
    api = new FakeApi();
    history = new FakeHistory();
    jasmine.addMatchers(customMatchers);
  });

  function dispatch(action) {
    actions.push(action);
  }

  function getState() {
    return {
      dataSetMenu: {
        reportDataId: 7,
      },
    };
  }

  it('handles the correct page happy path', promiseTest(async () => {
    spyOn(api, 'getFilters').and.returnValue(Promise.resolve({
      default_filter: {
        date_time: ["01/01/2014", "06/01/2016"],
      },
      help: {
        tags: true,
      },
      filters: [
        {
          filter: "tags",
          interface_type: "tags",
          display: "Tags",
        },
      ]
    }));
    spyOn(api, 'getDefaultReportName').and.returnValue(Promise.resolve({
      name: 'thereportname',
    }));
    spyOn(api, 'runTrialReport').and.returnValue(Promise.resolve([{}, {}]));
    await doLoadReportSetUp(7)
      (dispatch, getState, {api});
    // leave functions out of the comparison.
    expect(filter(actions, a => typeof a !== 'function')).toEqualActionList([
      markPageLoadingAction(true),
      startNewReportAction({
        defaultFilter: {
          date_time: ["01/01/2014", "06/01/2016"],
        },
        help: {
          tags: true,
        },
        filters: [
          {
            filter: "tags",
            interface_type: "tags",
            display: "Tags",
          },
        ],
        name: 'thereportname',
      }),
      updateRecordCount(2),
      markPageLoadingAction(false),
    ]);
  }));

  it('uses the given report filter', promiseTest(async () => {
    spyOn(api, 'getFilters').and.returnValue(Promise.resolve({
      default_filter: {},
      help: {
        tags: true,
      },
      filters: [
        {
          filter: "tags",
          interface_type: "tags",
          display: "Tags",
        },
      ]
    }));
    spyOn(api, 'getDefaultReportName').and.returnValue(Promise.resolve({
      name: 'thereportname',
    }));
    spyOn(api, 'runTrialReport').and.returnValue(Promise.resolve([{}, {}]));
    const givenFilter = {
      date_time: ["01/01/2014", "06/01/2016"],
    };
    await doLoadReportSetUp(7, givenFilter)
      (dispatch, getState, {api});
    // leave functions out of the comparison.
    expect(filter(actions, a => typeof a !== 'function')).toEqualActionList([
      markPageLoadingAction(true),
      startNewReportAction({
        defaultFilter: {
          date_time: ["01/01/2014", "06/01/2016"],
        },
        help: {
          tags: true,
        },
        filters: [
          {
            filter: "tags",
            interface_type: "tags",
            display: "Tags",
          },
        ],
        name: 'thereportname',
      }),
      updateRecordCount(2),
      markPageLoadingAction(false),
    ]);
  }));

  it('gives up early when the reportDataId does not ' +
    'match the data set menu', promiseTest(async () => {
    await doLoadReportSetUp(8)(dispatch, getState, {api});
    expect(filter(actions, a => typeof a !== 'function')).toEqual([
    ]);
  }));

  it('handles arbitrary errors', promiseTest(async () => {
    spyOn(api, 'getFilters').and.throwError(new Error('Some error'));
    await doLoadReportSetUp(7)(dispatch, getState, {api});
    expect(actions).toEqualActionList([
      markPageLoadingAction(true),
      markPageLoadingAction(false),
      errorAction("Some error"),
    ]);
  }));
});


describe('doRunReport', () => {
  let actions;
  let idGen;
  let api;

  beforeEach(() => {
    actions = [];
    idGen = new IdGenerator();
    api = new FakeApi();
  });

  function dispatch(action) {
    actions.push(action);
  }

  function getState() {
    return {};
  }

  it('handles the happy path', promiseTest(async () => {
    spyOn(api, 'runReport').and.returnValue(Promise.resolve({id: 99}));
    spyOn(api, 'listReports').and.returnValue(Promise.resolve([
      {id: 3, name: 'c', report_type: 3},
      {id: 4, name: 'd', report_type: 4},
    ]));
    const filter = {
      a: [{value: 1}],
    };

    await doRunReport(2, 'a', filter)(dispatch, getState, {idGen, api});
    expect(api.runReport).toHaveBeenCalledWith(2, 'a', {a: [1]});
    expect(api.listReports).toHaveBeenCalled();
    expect(actions).toEqual([
      clearErrorsAction(),
      startRunningReportAction({order: 1, name: 'a'}),
      replaceReportsListAction([
        {id: 3, name: 'c', report_type: 3},
        {id: 4, name: 'd', report_type: 4},
      ]),
      removeRunningReportAction(1),
    ]);
  }));

  it('handles api failures', promiseTest(async () => {
    const error = new Error("API Error");
    error.data = {some: 'data'};
    error.response = {
      status: 400,
    };
    spyOn(api, 'runReport').and.throwError(error);
    await doRunReport(undefined, 'a')(dispatch, getState, {idGen, api});
    expect(actions).toEqual([
      clearErrorsAction(),
      startRunningReportAction({order: 1, name: 'a'}),
      removeRunningReportAction(1),
      errorAction("API Error", {some: 'data'}),
    ]);
  }));

  it('handles arbitrary failures', promiseTest(async () => {
    const error = new Error("Some Error");
    spyOn(api, 'runReport').and.throwError(error);
    await doRunReport(undefined, 'a')(dispatch, getState, {idGen, api});
    expect(actions).toEqual([
      clearErrorsAction(),
      startRunningReportAction({order: 1, name: 'a'}),
      removeRunningReportAction(1),
      errorAction("Some Error"),
    ]);
  }));
});


describe('doRefreshReport', () => {
  let actions;
  let api;

  beforeEach(() => {
    actions = [];
    api = new FakeApi();
  });

  function dispatch(action) {
    actions.push(action);
  }

  function getState() {
    return {};
  }

  it('handles the happy path', promiseTest(async () => {
    spyOn(api, 'refreshReport').and.returnValue(Promise.resolve({}));
    spyOn(api, 'listReports').and.returnValue(Promise.resolve([
      {id: 3, name: 'c', report_type: 3},
      {id: 4, name: 'd', report_type: 4},
    ]));

    await doRefreshReport(2)(dispatch, getState, {api});
    expect(api.refreshReport).toHaveBeenCalledWith(2);
    expect(api.listReports).toHaveBeenCalled();
    expect(actions).toEqual([
      startRefreshingReportAction(2),
      replaceReportsListAction([
        {id: 3, name: 'c', report_type: 3},
        {id: 4, name: 'd', report_type: 4},
      ]),
    ]);
  }));

  it('handles arbitrary failures', promiseTest(async () => {
    const error = new Error("Some Error");
    spyOn(api, 'refreshReport').and.throwError(error);
    await doRefreshReport(2)(dispatch, getState, {api});
    expect(actions).toEqual([
      startRefreshingReportAction(2),
      errorAction("Some Error"),
    ]);
  }));
});


describe('doGetHints', () => {
  let actions;
  let idGen;
  let api;

  beforeEach(() => {
    actions = [];
    idGen = new IdGenerator();
    api = new FakeApi();
  });

  function dispatch(action) {
    actions.push(action);
  }

  function getState() {
    return {};
  }

  it('handles the happy path', promiseTest(async () => {
    spyOn(api, 'getHelp').and.returnValue(Promise.resolve([
      {value: 3, display: 'Red'},
      {value: 4, display: 'Blue'},
    ]));
    const filter = {
      a: [{value: 1}],
    }
    await doGetHelp(9, filter, 'labels', 'z')(dispatch, getState, {api});
    expect(api.getHelp).toHaveBeenCalledWith(9, {a: [1]}, 'labels', 'z');
    expect(actions).toEqual([
      markFieldLoadingAction('labels', true),
      clearHintsAction('labels'),
      receiveHintsAction('labels', [
        {value: 3, display: 'Red'},
        {value: 4, display: 'Blue'},
      ]),
      markFieldLoadingAction('labels', false),
    ]);
  }));

  it('handles arbitrary failures', promiseTest(async () => {
    const error = new Error("Some Error");
    spyOn(api, 'getHelp').and.throwError(error);
    await doGetHelp(9, {}, 'labels')(dispatch, getState, {api});
    expect(actions).toEqual([
      markFieldLoadingAction('labels', true),
      clearHintsAction('labels'),
      errorAction("Some Error"),
      markFieldLoadingAction('labels', false),
    ]);
  }));
});


describe('getFilterValuesOnly', () => {
  it('returns strings and plain objects unchanged', () => {
    const filter = {a: 'b', c: {d: 'e'}};
    expect(getFilterValuesOnly(filter)).toEqual(filter);
  });

  it('returns date ranges unchanged', () => {
    const filter = {a: ['11/11/1111', '12/22/2222']};
    expect(getFilterValuesOnly(filter)).toEqual(filter);
  });

  it('passes through empty arrays', () => {
    const filter = {a: []};
    expect(getFilterValuesOnly(filter)).toEqual(filter);
  });

  it('returns or filters stripped down to their values', () => {
    const filter = {a: [{value: 1}]};
    expect(getFilterValuesOnly(filter)).toEqual({a: [1]});
  });

  it('returns and/or filters stripped down to their values', () => {
    const filter = {a: [[{value: 1}]]};
    expect(getFilterValuesOnly(filter)).toEqual({a: [[1]]});
  });
});


describe('doUpdateFilterWithDependencies end to end', () => {
  let actions;
  let idGen;
  let api;
  let store;
  let newReportState;
  let oldReportState;

  const defaultState = {
    reportState: {
      filterInterface: [
        {filter: 'locations'},
        {filter: 'contact'},
        {filter: 'partner'},
      ],

      currentFilterDirty: true,
      currentFilter: {
        'locations': {city: 'Indy', state: 'IN'},
        'contact': [
          {value: 3},
          {value: 4},
        ],
        'partner': [
          {value: 5},
          {value: 6},
        ],
      },
      recordCount: 0,
    },
  };

  beforeEach(promiseTest(async () => {
    actions = [];
    idGen = new IdGenerator();
    api = new FakeApi();

    spyOn(api, 'getHelp').and.callFake((_r, _f, field) => {
      switch(field) {
        case 'state':
          return Promise.resolve([{value: 'CA'}]);
        case 'partner':
          return Promise.resolve([{value: 5}]);
        case 'contact':
          return Promise.resolve([{value: 3}]);
      }
    });
    spyOn(api, 'runTrialReport').and.returnValue(Promise.resolve([{}, {}]));

    store = createReduxStore(
      combineReducers({reportState: reportStateReducer}),
      defaultState,
      {api, idGen});

    store.dispatch(
      setSimpleFilterAction('locations', {city: 'Indy2', state: 'IN'}));
    await store.dispatch(
      doUpdateFilterWithDependencies(
        defaultState.reportState.filterInterface, 0));

    newReportState = store.getState().reportState;
    oldReportState = defaultState.reportState;
  }));

  it('has the expected hints', promiseTest(async () => {
    expect(newReportState.hints).toEqual({
      state: [{value: 'CA'}],
      partner: [{value: 5}],
      contact: [{value: 3}],
    });
  }));

  it('has the expected filterInterface', promiseTest(async () => {
    expect(newReportState.filterInterface)
      .toEqual(oldReportState.filterInterface);
  }));

  it('has the expected currentFilter', promiseTest(async () => {
    expect(newReportState.currentFilter).toEqual({
      ...oldReportState.currentFilter,
      locations: {city: 'Indy2', state: 'IN'},
      contact: [{value: 3}],
    });
    expect(newReportState.currentFilterDirty).toEqual(false);
  }));

  it('has the expected recordCount', promiseTest(async () => {
    expect(newReportState.recordCount).toEqual(2);
  }));
});

describe('doUpdateFilterWithDependencies vs clean filter', () => {
  let actions;

  beforeEach(() => {
    actions = [];
  });

  function dispatch(action) {
    actions.push(action);
  }

  function getState() {
    return {
      reportState: {
        currentFilterDirty: false,
      },
    };
  }

  it('does nothing', promiseTest(async () => {
    const api = new FakeApi();
    await doUpdateFilterWithDependencies()(dispatch, getState, {api});
    expect(actions).toEqual([]);
  }));
});

describe('runTrialReport', () => {
  const filter = {
    'locations': {city: 'Indy', state: 'IN'},
    'contact': [
      {value: 3},
      {value: 4},
    ],
    'partner': [
      {value: 5},
      {value: 6},
    ],
  };
  let api;

  beforeEach(() => {
    api = new FakeApi();
  });


  it('has a working happy path', promiseTest(async () => {
    spyOn(api, 'runTrialReport').and.returnValue(Promise.resolve([{}, {}]));
    const result = await runTrialReport(api, 3, filter, []);
    expect(api.runTrialReport).toHaveBeenCalledWith(
      3,
      getFilterValuesOnly(filter),
      []);
    expect(result).toEqual([{}, {}]);
  }));
});
