import React, {PropTypes, Component} from 'react';
import {connect} from 'react-redux';
import {map} from 'lodash-compat';
import {setCookie} from 'common/cookie';
import PopMenu from 'common/ui/PopMenu';
import classnames from 'classnames';

import {
  doRefreshReport,
  doSetUpForClone,
} from '../actions/compound-actions';


class ReportList extends Component {
  constructor() {
    super();
    this.state = {
      currentlyActive: '',
    };
  }

  clickMenu(e) {
    const {currentlyActive: oldActiveId} = this.state;
    const activeId = e.target.parentNode.parentNode.id;

    // Hide if they clicked the same one. Important for IE8.
    const currentlyActive = oldActiveId === activeId ? '' : activeId;
    this.setState({currentlyActive});
  }

  handleRefreshReport(report) {
    const {dispatch} = this.props;
    dispatch(doRefreshReport(report.order));
    this.closeAllPopups();
  }

  handlePreviewReport(report) {
    const {history} = this.props;
    const href = '/preview/' + report.order;
    const query = {
      reportName: report.name,
      reportType: report.report_type,
    };
    this.closeAllPopups();
    history.pushState(null, href, query);
  }

  handleExportReport(report) {
    const {history} = this.props;
    const href = '/export/' + report.order;
    this.closeAllPopups();
    history.pushState(null, href);
  }

  handleCreateNewReport(e) {
    const {history} = this.props;
    e.preventDefault();
    history.pushState('/');
  }

  handleSwitchVersions() {
    setCookie('reporting_version', 'classic');
    window.location.assign('/reports/view/overview');
  }

  async handleCloneReport(report) {
    const {dispatch, history} = this.props;
    this.closeAllPopups();
    dispatch(doSetUpForClone(history, report.order));
  }

  closeAllPopups() {
    this.setState({currentlyActive: ''});
  }

  render() {
    const {reports, highlightId} = this.props;
    const {currentlyActive} = this.state;
    const reportLinks = map(reports, r => {
      const options = [];
      const numberedID = 'listentry' + r.id;
      let isThisMenuActive = false;
      if (numberedID === currentlyActive) {
        isThisMenuActive = true;
      }
      if (r.report_type && r.id) {
        options.push({
          display: 'Preview',
          onSelect: () => {this.handlePreviewReport(r);},
        });
      }
      if (r.id) {
        options.push({
          display: 'Export',
          onSelect: () => {this.handleExportReport(r);},
        }, {
          display: 'Refresh',
          onSelect: () => {this.handleRefreshReport(r);},
        });
        options.push({
          display: 'Clone',
          onSelect: () => {this.handleCloneReport(r);},
        });
      }
      return (
        <li
          className={classnames(
            highlightId === r.id ? 'active' : '',
            numberedID === currentlyActive ? 'active-parent' : '',
          )}
          key={r.id}
          id={numberedID}>
          {options.length > 0 ?
            <PopMenu options={options}
              isMenuActive={isThisMenuActive}
              toggleMenu={(e) => this.clickMenu(e)}
              closeAllPopups={(e) => this.closeAllPopups(e)} />
              : ''}
          {(r.isRunning || r.isRefreshing) ?
            <span className="report-loader"></span>
            : ''}
          <span className="menu-text">{r.name}</span>
        </li>
      );
    });

    return (
      <div>
        <div className="sidebar reporting">
          <h2 className="top">Saved Reports</h2>
          <button
            className="button primary wide"
            onClick={e => this.handleCreateNewReport(e)}>
            Create a New Report
          </button>
          <div className="report-list">
            <ul>
              {reportLinks}
            </ul>
          </div>
          <h2>Reporting Version</h2>
          <button
            className="button primary wide"
            onClick={() => this.handleSwitchVersions()}>
            Switch to Classic Reporting
          </button>
        </div>
      </div>
    );
  }
}

ReportList.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  reports: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      order: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      report_type: PropTypes.string,
      isRunning: PropTypes.bool.isRequired,
    }),
  ).isRequired,
  highlightId: PropTypes.number,
};

export default connect(s => ({
  reports: s.reportList.reports,
  highlightId: s.reportList.highlightId,
}))(ReportList);
