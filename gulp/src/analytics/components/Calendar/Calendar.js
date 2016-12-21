import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doSetSelectedMonth} from '../../actions/calendar-actions';
import {doSetSelectedYear} from '../../actions/calendar-actions';
import {doSetSelectedDay} from '../../actions/calendar-actions';
import {doSetSelectedRange} from '../../actions/calendar-actions';
import CalendarPanel from 'common/ui/CalendarPanel';
import RangeSelection from './RangeSelection';

class Calendar extends Component {
  constructor(props) {
    super(props);

    this.state = {
      showCalendar: false,
    };
  }
  setRangeSelection(range) {
    const {dispatch, analytics} = this.props;
    const startRange = range[0];
    const endRange = range[1];
    const activeMainDimension = analytics.activePrimaryDimension;
    const activeFilters = analytics.activeFilters;
    dispatch(doSetSelectedRange(startRange, endRange, activeMainDimension, activeFilters));
  }
  showCalendar() {
    this.setState({
      showCalendar: true,
    });
  }
  updateMonth(month) {
    const updatedMonth = (month - 1);
    const {dispatch} = this.props;
    dispatch(doSetSelectedMonth(updatedMonth));
  }
  updateYear(year) {
    const {dispatch} = this.props;
    dispatch(doSetSelectedYear(year));
  }
  generateYearChoices() {
    const now = new Date();
    const numberOfYears = 50;
    let offset = 0;
    // how many years should come before and after the current year
    const pivot = numberOfYears % 2 === 0 ? numberOfYears - 1 : numberOfYears;
    offset = Math.floor(pivot / 2);
    const startYear = now.getFullYear() + offset;

    const yearChoices = [];
    for (let i = 0; i < numberOfYears; i++) {
      yearChoices.push({
        value: (startYear - i),
        display: (startYear - i).toString(),
      });
    }
    return yearChoices;
  }
  daySelected(day) {
    const {dispatch} = this.props;
    dispatch(doSetSelectedDay(day));
  }
  render() {
    const {analytics, showCalendarRangePicker, hideCalendarRangePicker, onMouseDown, onMouseUp} = this.props;
    const day = analytics.day;
    const month = analytics.month;
    const year = analytics.year;

    const calendar = ( <CalendarPanel
                      year={year}
                      month={month}
                      day={day}
                      onYearChange={y => this.updateYear(y)}
                      onMonthChange={m => this.updateMonth(m)}
                      onSelect={d => this.daySelected(d)}
                      yearChoices={this.generateYearChoices()}
                    />);
    return (
      <div onMouseDown={onMouseDown} onMouseUp={onMouseUp} className={showCalendarRangePicker ? 'calendar-container active-picker' : 'calendar-container non-active-picker'}>
        <ul>
          <li className="calendar-pick full-calendar">
            <div className={this.state.showCalendar ? 'show-calendar' : 'hide-calendar'}>
              {calendar}
            </div>
            <RangeSelection cancelSelection={hideCalendarRangePicker} showCalendar={this.showCalendar.bind(this)} showCustomRange={() => this.showCalendar()} setRange={y => this.setRangeSelection(y)}/>
          </li>
        </ul>
      </div>
    );
  }
}


Calendar.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  analytics: React.PropTypes.object.isRequired,
  showCalendarRangePicker: React.PropTypes.bool,
  hideCalendarRangePicker: React.PropTypes.func,
  onMouseDown: React.PropTypes.func,
  onMouseUp: React.PropTypes.func,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(Calendar);
