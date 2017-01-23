import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doSetSelectedEndMonth} from '../../actions/calendar-actions';
import {doSetSelectedEndYear} from '../../actions/calendar-actions';
import {doSetSelectedEndDay} from '../../actions/calendar-actions';
import {doSetSelectedStartMonth} from '../../actions/calendar-actions';
import {doSetSelectedStartYear} from '../../actions/calendar-actions';
import {doSetSelectedStartDay} from '../../actions/calendar-actions';
import {doSetSelectedRange} from '../../actions/calendar-actions';
import {doSetCustomRange} from '../../actions/calendar-actions';
import CalendarPanel from 'common/ui/CalendarPanel';
import HelpText from 'common/ui/HelpText';
import RangeSelection from './RangeSelection';

class Calendar extends Component {
  constructor(props) {
    super(props);

    this.state = {
      showCalendar: false,
      errorMessage: false,
    };

    this.showCalendar = this.showCalendar.bind(this);
    this.mouseUpHandler = this.mouseUpHandler.bind(this);
    this.mouseDownHandler = this.mouseDownHandler.bind(this);
  }
  componentDidMount() {
    window.addEventListener('mousedown', this.pageClick.bind(this), false);
  }
  setRangeSelection(range) {
    const {dispatch, analytics, hideCalendarRangePicker} = this.props;
    const startRange = range[0];
    const endRange = range[1];
    let activeFilters;
    analytics.navigation.map((nav) => {
      if (nav.active) {
        activeFilters = nav.activeFilters;
      }
    });
    const activeMainDimension = analytics.activePrimaryDimension;
    dispatch(doSetSelectedRange(startRange, endRange, activeMainDimension, activeFilters));
    this.setState({
      showCalendar: false,
    });
    hideCalendarRangePicker();
  }
  pageClick() {
    if (this.mouseIsDownOnCalendar) {
      return;
    }
    this.setState({
      showCalendar: false,
    });
  }
  mouseDownHandler() {
    this.mouseIsDownOnCalendar = true;
  }
  mouseUpHandler() {
    this.mouseIsDownOnCalendar = false;
  }
  showCalendar() {
    this.setState({
      showCalendar: true,
    });
  }
  updateStartMonth(month) {
    const updatedMonth = (month - 1);
    const {dispatch} = this.props;
    dispatch(doSetSelectedStartMonth(updatedMonth));
  }
  updateStartYear(year) {
    const {dispatch} = this.props;
    dispatch(doSetSelectedStartYear(year));
  }
  updateEndMonth(month) {
    const updatedMonth = (month - 1);
    const {dispatch} = this.props;
    dispatch(doSetSelectedEndMonth(updatedMonth));
  }
  updateEndYear(year) {
    const {dispatch} = this.props;
    dispatch(doSetSelectedEndYear(year));
  }
  generateYearChoices() {
    const now = new Date();
    const numberOfYears = 50;
    // how many years should come before and after the current year
    const startYear = now.getFullYear();

    const yearChoices = [];
    for (let i = 0; i < numberOfYears; i++) {
      yearChoices.push({
        value: (startYear - i),
        display: (startYear - i).toString(),
      });
    }
    return yearChoices;
  }
  endDaySelected(day) {
    const {dispatch} = this.props;
    dispatch(doSetSelectedEndDay(day));
  }
  startDaySelected(day) {
    const {dispatch} = this.props;
    dispatch(doSetSelectedStartDay(day));
  }
  applyCustomRange() {
    const {dispatch, analytics, hideCalendarRangePicker} = this.props;
    const startDate = `${analytics.startMonth + 1}/${analytics.startDay}/${analytics.startYear}`;
    const endDate = `${analytics.endMonth + 1}/${analytics.endDay}/${analytics.endYear}`;
    let activeFilters;
    analytics.navigation.map((nav) => {
      if (nav.active) {
        activeFilters = nav.activeFilters;
      }
    });
    if (Date.parse(startDate) < Date.parse(endDate)) {
      const activeMainDimension = analytics.activePrimaryDimension;
      dispatch(doSetCustomRange(startDate, endDate, activeMainDimension, activeFilters));
      this.setState({
        showCalendar: false,
        errorMessage: false,
      });
      hideCalendarRangePicker();
    } else {
      this.setState({
        showCalendar: true,
        errorMessage: true,
      });
    }
  }
  render() {
    const {analytics, showCalendarRangePicker, hideCalendarRangePicker, onMouseDown, onMouseUp} = this.props;
    const endDay = analytics.endDay;
    const endMonth = analytics.endMonth;
    const endYear = analytics.endYear;
    const startDay = analytics.startDay;
    const startMonth = analytics.startMonth;
    const startYear = analytics.startYear;
    const errorMessage = `INVALID DATE RANGE: Start Date must be before End Date`;

    const startCalendar = ( <CalendarPanel
                      year={startYear}
                      month={startMonth}
                      day={startDay}
                      onYearChange={y => this.updateStartYear(y)}
                      onMonthChange={m => this.updateStartMonth(m)}
                      onSelect={d => this.startDaySelected(d)}
                      yearChoices={this.generateYearChoices()}
                    />);
    const endCalendar = ( <CalendarPanel
                      year={endYear}
                      month={endMonth}
                      day={endDay}
                      onYearChange={y => this.updateEndYear(y)}
                      onMonthChange={m => this.updateEndMonth(m)}
                      onSelect={d => this.endDaySelected(d)}
                      yearChoices={this.generateYearChoices()}
                    />);
    return (
      <div onMouseDown={onMouseDown} onMouseUp={onMouseUp} className={showCalendarRangePicker ? 'calendar-container active-picker' : 'calendar-container non-active-picker'}>
        <ul>
          <li className="calendar-pick full-calendar">
            <div onMouseDown={this.mouseDownHandler} onMouseUp={this.mouseUpHandler} className={this.state.showCalendar ? 'show-calendar' : 'hide-calendar'}>
              {this.state.errorMessage ? <HelpText message={errorMessage}/> : ''}
              <div className="start-calendar">
                <p className="date-label">Start Date</p>
                {startCalendar}
              </div>
              <div className="end-calendar">
                <p className="date-label">End Date</p>
                {endCalendar}
              </div>
            </div>
            <RangeSelection applySelection={() => this.applyCustomRange()} cancelSelection={hideCalendarRangePicker} showCalendar={this.showCalendar} showCustomRange={() => this.showCalendar()} setRange={y => this.setRangeSelection(y)}/>
          </li>
        </ul>
      </div>
    );
  }
}


Calendar.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  analytics: React.PropTypes.object.isRequired,
  /**
   * Boolean true or false determining whether the calendar is shown or not
   */
  showCalendarRangePicker: React.PropTypes.bool,
  /**
   * Function for hiding teh calendar
   */
  hideCalendarRangePicker: React.PropTypes.func,
  /**
   * Mousedown on the calendar to keep the calendar displayed when clicking on it
   */
  onMouseDown: React.PropTypes.func,
  /**
   * Mouseup on the calendar to keep it displayed when click inside of it
   */
  onMouseUp: React.PropTypes.func,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(Calendar);
