import reportStateReducer, {
  withFilterDirtied,
} from '../reducers/report-state-reducer';

import {
  startNewReportAction,
  setSimpleFilterAction,
  addToOrFilterAction,
  removeFromOrFilterAction,
  addToAndOrFilterAction,
  removeFromAndOrFilterAction,
  deleteFilterAction,
  emptyFilterAction,
  unlinkFilterAction,
  setReportNameAction,
  receiveHintsAction,
  clearHintsAction,
  resetCurrentFilterDirty,
  updateRecordCount,
} from '../actions/report-state-actions';

describe('reportStateReducer', () => {
  describe('default state', () => {
    const result = reportStateReducer(undefined, {});
    it('has a current filter', () => {
      expect(result.currentFilter).toEqual({});
    });
    it('has a filter interface', () => {
      expect(result.filterInterface).toEqual([]);
    });
    it('has a name', () => {
      expect(result.reportName).toEqual('');
    });
    it('has hints', () => {
      expect(result.hints).toEqual({});
    });
  });

  describe('startNewReportAction', () => {
    const action = startNewReportAction({
      defaultFilter: {1: 2},
      help: {3: 4},
      filters: {5: 6},
      name: 'zz',
    });
    const result = reportStateReducer(null, action);
    it('puts data where it goes', () => {
      expect(result).toEqual({
        filterInterface: {5: 6},
        help: {3: 4},
        currentFilter: {1: 2},
        currentFilterDirty: false,
        errors: {},
        hints: {},
        reportName: 'zz',
        isValid: true,
      });
    });
  });

  it('can merge a scalar filter', () => {
    const action = setSimpleFilterAction("city", {value: 2, display: "Clay"});
    const result = reportStateReducer({
      currentFilter: {},
      currentFilterDirty: false,
    }, action);
    expect(result).toEqual({
      currentFilter: {
        city: {value: 2, display: "Clay"},
      },
      currentFilterDirty: true,
    });
  });

  it('can update the record count', () => {
    const action = updateRecordCount(3);
    const result = reportStateReducer({recordCount: 0}, action);
    expect(result).toEqual({recordCount: 3});
  });

  it('deletes simple filters set to undefined', () => {
    const action = setSimpleFilterAction("city", undefined);
    const result = reportStateReducer({
      currentFilter: {
        city: "Heresville",
      },
      currentFilterDirty: false,
    }, action);
    expect(result).toEqual({
      currentFilter: {},
      currentFilterDirty: true,
    });
  });

  it('can add to an or filter', () => {
    const action = addToOrFilterAction(
      "contact", [{value: 3, display: "Bob"}, {value: 5, display: "Rex"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "contact": [
          {value: 4, display: "Ann"},
        ],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: true,
      currentFilter: {
        "contact": [
          {value: 4, display: "Ann"},
          {value: 3, display: "Bob"},
          {value: 5, display: "Rex"},
        ],
      },
    });
  });

  it('can add to an or filter if that filter does not yet exist', () => {
    const action = addToOrFilterAction(
      "contact", [{value: 3, display: "Bob"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {},
    }, action);
    expect(result).toEqual({
      currentFilterDirty: true,
      currentFilter: {
        "contact": [
          {value: 3, display: "Bob"},
        ],
      }
    });
  });

  it('can overwrite a value by adding to an or filter', () => {
    const action = addToOrFilterAction(
      "contact", [{value: 3, display: "Bob"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "contact": [
          {value: 3, display: "Dan"},
          {value: 4, display: "Ann"},
        ],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: true,
      currentFilter: {
        "contact": [
          {value: 4, display: "Ann"},
          {value: 3, display: "Bob"},
        ],
      },
    });
  });

  it('can remove values from an or filter', () => {
    const action = removeFromOrFilterAction(
      "contact", [{value: 3, display: "Bob"}, {value: 5, display: "Rex"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "contact": [
          {value: 3, display: "Bob"},
          {value: 4, display: "Ann"},
          {value: 5, display: "Rex"},
        ],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: true,
      currentFilter: {
        "contact": [
          {value: 4, display: "Ann"},
        ],
      },
    });
  });

  it('can leave an or filter untouched when removing ' +
      'an item that is not there.', () => {
    const action = removeFromOrFilterAction(
      "contact", [{value: 3, display: "Bob"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "contact": [
          {value: 4, display: "Ann"},
        ],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: false,
      currentFilter: {
        "contact": [
          {value: 4, display: "Ann"},
        ],
      },
    });
  });

  it('can ignore removing an item from a mising filter', () => {
    const action = removeFromOrFilterAction(
      "contact", [{value: 3, display: "Bob"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {},
    }, action);
    expect(result).toEqual({
      currentFilterDirty: false,
      currentFilter: {},
    });
  });

  it('leaves behind an empty or filter after remove', () => {
    const action = removeFromOrFilterAction(
      "contact", [{value: 3, display: "Bob"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "contact": [
          {value: 3, display: "Whatever"},
        ],
      },
    }, action);
    expect(result).toDiffEqual({
      currentFilterDirty: true,
      currentFilter: {
        "contact": [],
      },
    });
  });

  it('can add an item to an and/or filter', () => {
    const action = addToAndOrFilterAction(
      "tags", 0, [{value: 3, display: "Test"}, {value: 2, display: "Test2"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [[]],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: true,
      currentFilter: {
        "tags": [
          [
            {value: 3, display: "Test"},
            {value: 2, display: "Test2"},
          ],
        ],
      },
    });
  });

  it('can add an item to an and/or filter if the filter did not exist', () => {
    const action = addToAndOrFilterAction(
      "tags", 10, [{value: 3, display: "Test"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {},
    }, action);
    expect(result).toEqual({
      currentFilterDirty: true,
      currentFilter: {
        "tags": [
          [
            {value: 3, display: "Test"},
          ],
        ],
      },
    });
  });

  it('can add an item to an and/or filter if the row did not exist', () => {
    const action = addToAndOrFilterAction(
      "tags", 10, [{value: 3, display: "Test"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [
          [
            {value: 1, display: "Red"},
          ],
        ],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: true,
      currentFilter: {
        "tags": [
          [
            {value: 1, display: "Red"},
          ],
          [
            {value: 3, display: "Test"},
          ],
        ],
      },
    });
  });

  it('can remove an item from an and/or filter', () => {
    const action = removeFromAndOrFilterAction(
      "tags", 0, [{value: 3, display: "Test"}, {value:2, display: "Test2"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [
          [
            {value: 3, display: "Test"},
            {value: 2, display: "Test2"},
            {value: 1, display: "Red"},
          ],
        ],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: true,
      currentFilter: {
        "tags": [
          [
            {value: 1, display: "Red"},
          ],
        ],
      },
    });
  })

  it('can leave an and/or filter untouched when removing ' +
      'an item that is not there.', () => {
    const action = removeFromAndOrFilterAction(
      "tags", 0, [{value: 3, display: "Test"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [
          [
            {value: 1, display: "Red"},
          ],
        ],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [
          [
            {value: 1, display: "Red"},
          ],
        ],
      },
    });
  });

  it('can leave an and/or filter untouched when removing ' +
      'from a row that is not there.', () => {
    const action = removeFromAndOrFilterAction(
      "tags", 10, [{value: 3, display: "Test"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [
          [
            {value: 1, display: "Red"},
          ],
        ],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [
          [
            {value: 1, display: "Red"},
          ],
        ],
      },
    });
  });

  it('automatically deletes an empty and/or row after remove', () => {
    const action = removeFromAndOrFilterAction(
      "tags", 0, [{value: 3, display: "Test"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [
          [
            {value: 3, display: "Test"},
          ],
          [
            {value: 1, display: "Red"},
          ],
        ],
      },
    }, action);
    expect(result).toEqual({
      currentFilterDirty: true,
      currentFilter: {
        "tags": [
          [
            {value: 1, display: "Red"},
          ],
        ],
      },
    });
  });

  it('leaves behind an empty and/or filter after remove', () => {
    const action = removeFromAndOrFilterAction(
      "tags", 0, [{value: 3, display: "Test"}]);
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [
          [
            {value: 3, display: "Test"},
          ],
        ],
      },
    }, action);
    expect(result).toDiffEqual({
      currentFilterDirty: true,
      currentFilter: {
        "tags": [],
      },
    });
  });

  it('clears a filter on demand', () => {
    const action = deleteFilterAction("tags");
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {
        "tags": [],
      },
    }, action);
    expect(result).toDiffEqual({
      currentFilterDirty: true,
      currentFilter: {},
    });
  });

  it('empties a filter', () => {
    const action = emptyFilterAction("tags");
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {},
    }, action);
    expect(result).toDiffEqual({
      currentFilterDirty: true,
      currentFilter: {
        "tags": [],
      },
    });
  });

  it('unlinks a filter', () => {
    const action = unlinkFilterAction("tags");
    const result = reportStateReducer({
      currentFilterDirty: false,
      currentFilter: {},
    }, action);
    expect(result).toDiffEqual({
      currentFilterDirty: true,
      currentFilter: {
        "tags": {nolink: true},
      },
    });
  });

  it('can set the report name', () => {
    const action = setReportNameAction("Contacts 2016");
    const result = reportStateReducer({}, action);
    expect(result.reportName).toEqual("Contacts 2016");
  });

  it('caps the report name at 24 characters', () => {
    const action = setReportNameAction("123456789012345678901234567890");
    const result = reportStateReducer({}, action);
    expect(result.reportName).toEqual("123456789012345678901234");
  });

  it('can receive hints', () => {
    const action = receiveHintsAction("city", [{value: 3, display: "Indy"}]);
    const result = reportStateReducer({
      hints: {},
    }, action);
    expect(result.hints).toEqual({city: [{value: 3, display: "Indy"}]});
  });

  it('can clear hints', () => {
    const action = clearHintsAction("city");
    const result= reportStateReducer({
      hints: {
        city: [1, 2, 3],
      },
    }, action);
    expect(result.hints).toEqual({});
  });

  it('can reset the currentFilterDirty flag', () => {
    const action = resetCurrentFilterDirty();
    const result = reportStateReducer({
      currentFilterDirty: true,
    }, action);
    expect(result).toEqual({
      currentFilterDirty: false,
    });
  });
});


describe('withFilterDirtied', () => {
  it('does nothing when currentFilter is unchanged', () => {
    const oldState = {
      currentFilter: {1: 2},
    };
    const newState = {
      currentFilter: {1: 2},
    };
    const result = withFilterDirtied(oldState, newState);
    expect(result).toEqual(newState);
  });

  it('sets currentFilterDirty when currentFilter changes', () => {
    const oldState = {
      currentFilter: {1: 2},
      currentFilterDirty: false,
    };
    const newState = {
      currentFilter: {1: 3},
      currentFilterDirty: false,
    };
    const result = withFilterDirtied(oldState, newState);
    expect(result).toEqual({...newState, currentFilterDirty: true});
  });
});
