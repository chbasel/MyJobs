import {
  ReportFinder,
  ReportConfiguration,
} from '../reportEngine';

import {promiseTest} from '../../util/spec';


class FakeBuilder {
  build(name, rpId, filters) {
    return {name: name, rpId: rpId, filters: filters};
  }
}

const fakeApi = {
  getReportingTypes: () => [1],
  getReportTypes: () => [2],
  getDataTypes: () => [3],
  getPresentationTypes: () => [4],
  getFilters: () => ({filters: {6: 6}}),
  getHelp: () =>
    [{'city': 'Indianapolis'}, {'city': 'Chicago'}],
  getDefaultReportName: () => ({'name': 'zzz'}),
  runReport: () => ({'ok': 7}),
};

describe('ReportFinder', () => {
  const finder = new ReportFinder(
    fakeApi,
    new FakeBuilder());

  it('can get reporting types', promiseTest(async () => {
    expect(await finder.getReportingTypes()).toEqual([1]);
  }));


  it('can build a ReportConfiguration', promiseTest(async () => {
    expect(await finder.buildReportConfiguration(2)).toEqual(
      {rpId: 2, filters: {6: 6}, name: 'zzz'});
  }));

  describe('subscriptions', () => {
    let newId = null;
    const ref = finder.subscribeToReportList((id) => { newId = id; });

    it('can inform subscribers of new reports', () => {
      finder.noteNewReport(22);
      expect(newId).toEqual(22);
    });

    it('can unsubscribe', () => {
      finder.unsubscribeToReportList(ref);
      finder.noteNewReport(33);
      expect(newId).toEqual(22);
    });
  });
});

describe('ReportConfiguration', () => {
  let config;
  let fakeComponent;

  class FakeComponent {
    newReportNote() {}
  }

  beforeEach(() => {
    fakeComponent = new FakeComponent();
    config = new ReportConfiguration(
      'defaultName', 2, {}, fakeApi,
      id => fakeComponent.newReportNote(id));
  });

  it('can get help', promiseTest(async () => {
    expect(await config.getHints('city', 'i')).toEqual(
      [{'city': 'Indianapolis'}, {'city': 'Chicago'}]);
  }));

  it('can remember changes to filters', () => {
    config.setFilter('city', 'Indianapolis');
    expect(config.getFilter()).toEqual({
      city: 'Indianapolis',
    });
  });


  it('treats blank filter values as removal', () => {
    config.setFilter('city', 'Indianapolis');
    config.setFilter('city', '');
    expect(config.getFilter()).toEqual({});
  });

  it('treats null filter values as removal', () => {
    config.setFilter('city', 'Indianapolis');
    config.setFilter('city', null);
    expect(config.getFilter()).toEqual({});
  });

  it('treats undefined filter values as removal', () => {
    config.setFilter('city', 'Indianapolis');
    config.setFilter('city', undefined);
    expect(config.getFilter()).toEqual({});
  });

  it('can remember changes to multifilters', () => {
    config.addToMultifilter('tag', {key: 'blue', display: 'Blue'});
    expect(config.getFilter()).toEqual({
      tag: ['blue'],
    });
  });

  it("won't add dups in multifilters", () => {
    config.addToMultifilter('tag', {key: 'blue', display: 'Blue'});
    config.addToMultifilter('tag', {key: 'blue', display: 'Blue'});
    expect(config.getFilter()).toEqual({
      tag: ['blue'],
    });
  });

  it('can remove items from multifilters', () => {
    config.addToMultifilter('tag', {key: 'red', display: 'Red'});
    config.addToMultifilter('tag', {key: 'blue', display: 'Blue'});
    config.removeFromMultifilter('tag', {key: 'red'});
    config.removeFromMultifilter('tag', {key: 'red'});
    expect(config.getFilter()).toEqual({
      tag: ['blue'],
    });
  });

  it('can remember and/or filters', () => {
    config.addToAndOrFilter('tag', 0, {key: 'red', display: 'Red'});
    expect(config.getFilter()).toEqual({
      tag: [['red']],
    });
  });

  it('can remove items from and/or filters', () => {
    config.addToAndOrFilter('tag', 0, {key: 'red', display: 'Red'});
    config.addToAndOrFilter('tag', 0, {key: 'blue', display: 'Blue'});
    config.removeFromAndOrFilter('tag', 0, {key: 'red'});
    config.removeFromAndOrFilter('tag', 0, {key: 'red'});
    expect(config.getFilter()).toEqual({
      tag: [['blue']],
    });
  });

  it('can return sane data for missing and/or filters', () => {
    expect(config.getAndOrFilter('tag')).toEqual([]);
  });

  it('removes empty tag lists on demand for and/or filters', () => {
    config.addToAndOrFilter('tag', 0, {key: 'red', display: 'Red'});
    config.addToAndOrFilter('tag', 1, {key: 'red', display: 'Red'});
    config.addToAndOrFilter('tag', 0, {key: 'blue', display: 'Blue'});
    config.removeFromAndOrFilter('tag', 0, {key: 'red'});
    config.removeFromAndOrFilter('tag', 0, {key: 'blue'});
    expect(config.getFilter()).toEqual({tag: [['red']]});
  });

  it('can run the report', promiseTest(async () => {
    spyOn(fakeApi, 'runReport').and.callThrough();
    spyOn(fakeComponent, 'newReportNote').and.callThrough();

    await config.run();

    expect(fakeApi.runReport).toHaveBeenCalledWith(2, 'defaultName', {});
    expect(fakeComponent.newReportNote).toHaveBeenCalled();
  }));

  it('can change the name of the report', promiseTest(async() => {
    spyOn(fakeApi, 'runReport').and.callThrough();
    spyOn(fakeComponent, 'newReportNote').and.callThrough();

    config.changeReportName('bbb');
    await config.run();

    expect(fakeApi.runReport).toHaveBeenCalledWith(2, 'bbb', {});
  }));

  it('notes name errors from api', promiseTest(async() => {
    fakeApi.runReport = () => ({'clienterrors': [
      {
        'field': 'name',
        'message': 'zzz',
      }]});
    fakeApi.runApi = () => ({
      message: 'yyy',
      field: 'name',
    });
    await config.run();

    expect(config.getReportNameErrors()).toContain('zzz');
  }));

  it('notes generic errors from api', promiseTest(async() => {
    fakeApi.runApi = () => ({
      message: 'yyy',
      field: 'name',
    });
    await config.run();

    expect(config.getReportNameErrors()).toContain('zzz');
  }));
});
