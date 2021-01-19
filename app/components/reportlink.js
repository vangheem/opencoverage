import { fmtRelativeDate } from '../utils'
import Link from 'next/link'

export default function ReportLink ({ report }) {
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
          '/report'
        }
      >
        <a>
          <strong>
            {report.organization}/{report.repo}
          </strong>{' '}
          <small>@ {report.branch}</small>{' '}
          <small>{fmtRelativeDate(report.modification_date)}</small>
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
          '/report'
        }
      >
        <a>
          <strong>
            {report.organization}/{report.repo}/pulls/{report.pull}
          </strong>{' '}
          <small>@ {report.branch}</small>{' '}
          <small>{fmtRelativeDate(report.modification_date)}</small>
        </a>
      </Link>
    )
  }
}
