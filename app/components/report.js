import { calcTagClassName, fmtNumber } from '../utils'
import ReportLink from './reportlink'

export default function Report ({ report }) {
  if (report.__type == 'CoverageReport') {
    return (
      <div className='box'>
        <article className='media'>
          <div className='media-content'>
            <div className='content'>
              <p>
                <ReportLink report={report} />
              </p>
              <p>
                Overall Coverage:
                <span
                  className={
                    'tag is-light ' + calcTagClassName(report.line_rate)
                  }
                >
                  {(report.line_rate * 100).toFixed(1)}%
                </span>
                - Covered lines:
                <span className='tag is-primary is-light'>
                  {fmtNumber(report.lines_covered)}
                </span>
                - Total lines:
                <span className='tag is-primary is-light'>
                  {fmtNumber(report.lines_valid)}
                </span>
              </p>
            </div>
          </div>
        </article>
      </div>
    )
  } else {
    return (
      <div className='box'>
        <article className='media'>
          <div className='media-content'>
            <div className='content'>
              <p>
                <ReportLink report={report} />
              </p>
              <p>
                Overall Coverage:
                <span
                  className={
                    'tag is-light ' +
                    calcTagClassName(report.coverage.line_rate)
                  }
                >
                  {(report.coverage.line_rate * 100).toFixed(1)}%
                </span>
                - Diff Coverage:
                <span
                  className={
                    'tag is-light ' + calcTagClassName(report.line_rate)
                  }
                >
                  {(report.line_rate * 100).toFixed(1)}%
                </span>
                - Covered lines:
                <span className='tag is-primary is-light'>
                  {fmtNumber(report.coverage.lines_covered)}
                </span>
                - Total lines:
                <span className='tag is-primary is-light'>
                  {fmtNumber(report.coverage.lines_valid)}
                </span>
              </p>
            </div>
          </div>
        </article>
      </div>
    )
  }
}
