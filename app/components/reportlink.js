import { fmtRelativeDate } from '../utils'
import Link from 'next/link'

export default function ReportLink ({ report }) {
  var project = report.project
  if (!project || project == '/') {
    project = ''
  }
  var projectLabel = <></>
  if (project) {
    projectLabel = <span className='tag is-warning is-light'>{project}</span>
  }
  if (report.__type == 'CoverageReport') {
    return (
      <Link
        href={
          '/' +
          report.organization +
          '/repos/' +
          report.repo +
          '/commits/' +
          report.commit_hash +
          '/report?project=' +
          project
        }
      >
        <a>
          <strong>
            {report.organization}/{report.repo}
          </strong>{' '}
          <small>@ {report.branch}</small>{' '}
          <small>{fmtRelativeDate(report.modification_date)}</small>
          {projectLabel}
        </a>
      </Link>
    )
  } else {
    return (
      <Link
        href={
          '/' +
          report.organization +
          '/repos/' +
          report.repo +
          '/pulls/' +
          report.pull +
          '/' +
          report.commit_hash +
          '/report?project=' +
          project
        }
      >
        <a>
          <strong>
            {report.organization}/{report.repo}/pulls/{report.pull}
          </strong>{' '}
          <small>@ {report.branch}</small>{' '}
          <small>{fmtRelativeDate(report.modification_date)}</small>
          {projectLabel}
        </a>
      </Link>
    )
  }
}
