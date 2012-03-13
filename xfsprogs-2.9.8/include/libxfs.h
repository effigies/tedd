/*
 * Copyright (c) 2000-2005 Silicon Graphics, Inc.
 * All Rights Reserved.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it would be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write the Free Software Foundation,
 * Inc.,  51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
#ifndef __LIBXFS_H__
#define __LIBXFS_H__

#define XFS_BIG_INUMS	1
#define XFS_BIG_BLKNOS	1

#include <xfs/platform_defs.h>

#include <pthread.h>
#include <xfs/list.h>
#include <xfs/cache.h>

#include <xfs/xfs_fs.h>
#include <xfs/xfs_types.h>
#include <xfs/xfs_arch.h>
#include <xfs/xfs_bit.h>
#include <xfs/xfs_inum.h>
#include <xfs/xfs_sb.h>
#include <xfs/xfs_ag.h>
#include <xfs/xfs_dir2.h>
#include <xfs/xfs_mount.h>
#include <xfs/xfs_da_btree.h>
#include <xfs/xfs_bmap_btree.h>
#include <xfs/xfs_alloc_btree.h>
#include <xfs/xfs_ialloc_btree.h>
#include <xfs/xfs_dir_sf.h>
#include <xfs/xfs_dir2_sf.h>
#include <xfs/xfs_attr_sf.h>
#include <xfs/xfs_dinode.h>
#include <xfs/xfs_inode.h>
#include <xfs/xfs_buf_item.h>
#include <xfs/xfs_inode_item.h>
#include <xfs/xfs_alloc.h>
#include <xfs/xfs_btree.h>
#include <xfs/xfs_bmap.h>


#ifndef XFS_SUPER_MAGIC
#define XFS_SUPER_MAGIC 0x58465342
#endif

#define xfs_isset(a,i)	((a)[(i)/(sizeof((a))*NBBY)] & (1<<((i)%(sizeof((a))*NBBY))))

/*
 * Argument structure for libxfs_init().
 */
typedef struct {
				/* input parameters */
	char            *volname;       /* pathname of volume */
	char            *dname;         /* pathname of data "subvolume" */
	char            *logname;       /* pathname of log "subvolume" */
	char            *rtname;        /* pathname of realtime "subvolume" */
	int             isreadonly;     /* filesystem is only read in applic */
	int             isdirect;       /* we can attempt to use direct I/O */
	int             disfile;        /* data "subvolume" is a regular file */        int             dcreat;         /* try to create data subvolume */
	int             lisfile;        /* log "subvolume" is a regular file */
	int             lcreat;         /* try to create log subvolume */
	int             risfile;        /* realtime "subvolume" is a reg file */        int             rcreat;         /* try to create realtime subvolume */
	int		setblksize;	/* attempt to set device blksize */
				/* output results */
	dev_t           ddev;           /* device for data subvolume */
	dev_t           logdev;         /* device for log subvolume */
	dev_t           rtdev;          /* device for realtime subvolume */
	long long       dsize;          /* size of data subvolume (BBs) */
	long long       logBBsize;      /* size of log subvolume (BBs) */
					/* (blocks allocated for use as
					 * log is stored in mount structure) */
	long long       logBBstart;     /* start block of log subvolume (BBs) */
	long long       rtsize;         /* size of realtime subvolume (BBs) */
	int		dbsize;		/* data subvolume device blksize */
	int		lbsize;		/* log subvolume device blksize */
	int		rtbsize;	/* realtime subvolume device blksize */
	int             dfd;            /* data subvolume file descriptor */
	int             logfd;          /* log subvolume file descriptor */
	int             rtfd;           /* realtime subvolume file descriptor */
} libxfs_init_t;

#define LIBXFS_EXIT_ON_FAILURE	0x0001	/* exit the program if a call fails */
#define LIBXFS_ISREADONLY	0x0002	/* disallow all mounted filesystems */
#define LIBXFS_ISINACTIVE	0x0004	/* allow mounted only if mounted ro */
#define LIBXFS_DANGEROUSLY	0x0008	/* repairing a device mounted ro    */
#define LIBXFS_EXCLUSIVELY	0x0010	/* disallow other accesses (O_EXCL) */
#define LIBXFS_DIRECT		0x0020	/* can use direct I/O, not buffered */

extern char	*progname;
extern int	libxfs_init (libxfs_init_t *);
extern void	libxfs_destroy (void);
extern int	libxfs_device_to_fd (dev_t);
extern dev_t	libxfs_device_open (char *, int, int, int);
extern void	libxfs_device_zero (dev_t, xfs_daddr_t, uint);
extern void	libxfs_device_close (dev_t);
extern int	libxfs_device_alignment (void);
extern void	libxfs_report(FILE *);

/* check or write log footer: specify device, log size in blocks & uuid */
typedef xfs_caddr_t (libxfs_get_block_t)(xfs_caddr_t, int, void *);

extern int	libxfs_log_clear (dev_t, xfs_daddr_t, uint, uuid_t *,
				int, int, int);
extern int	libxfs_log_header (xfs_caddr_t, uuid_t *, int, int, int,
				libxfs_get_block_t *, void *);


/*
 * Define a user-level mount structure with all we need
 * in order to make use of the numerous XFS_* macros.
 */
struct xfs_inode;
typedef struct xfs_mount {
	xfs_sb_t		m_sb;		/* copy of fs superblock */
	char			*m_fsname;	/* filesystem name */
	int			m_bsize;	/* fs logical block size */
	xfs_agnumber_t		m_agfrotor;	/* last ag where space found */
	xfs_agnumber_t		m_agirotor;	/* last ag dir inode alloced */
	xfs_agnumber_t		m_maxagi;	/* highest inode alloc group */
	uint			m_rsumlevels;	/* rt summary levels */
	uint			m_rsumsize;	/* size of rt summary, bytes */
	struct xfs_inode	*m_rbmip;	/* pointer to bitmap inode */
	struct xfs_inode	*m_rsumip;	/* pointer to summary inode */
	struct xfs_inode	*m_rootip;	/* pointer to root directory */
	dev_t			m_dev;
	dev_t			m_logdev;
	dev_t			m_rtdev;
	__uint8_t		m_dircook_elog;	/* log d-cookie entry bits */
	__uint8_t		m_blkbit_log;	/* blocklog + NBBY */
	__uint8_t		m_blkbb_log;	/* blocklog - BBSHIFT */
	__uint8_t		m_sectbb_log;	/* sectorlog - BBSHIFT */
	__uint8_t		m_agno_log;	/* log #ag's */
	__uint8_t		m_agino_log;	/* #bits for agino in inum */
	__uint16_t		m_inode_cluster_size;/* min inode buf size */
	uint			m_blockmask;	/* sb_blocksize-1 */
	uint			m_blockwsize;	/* sb_blocksize in words */
	uint			m_blockwmask;	/* blockwsize-1 */
	uint			m_alloc_mxr[2];	/* XFS_ALLOC_BLOCK_MAXRECS */
	uint			m_alloc_mnr[2];	/* XFS_ALLOC_BLOCK_MINRECS */
	uint			m_bmap_dmxr[2];	/* XFS_BMAP_BLOCK_DMAXRECS */
	uint			m_bmap_dmnr[2];	/* XFS_BMAP_BLOCK_DMINRECS */
	uint			m_inobt_mxr[2];	/* XFS_INOBT_BLOCK_MAXRECS */
	uint			m_inobt_mnr[2];	/* XFS_INOBT_BLOCK_MINRECS */
	uint			m_ag_maxlevels;	/* XFS_AG_MAXLEVELS */
	uint			m_bm_maxlevels[2]; /* XFS_BM_MAXLEVELS */
	uint			m_in_maxlevels;	/* XFS_IN_MAXLEVELS */
	xfs_perag_t		*m_perag;	/* per-ag accounting info */
	uint			m_flags;	/* global mount flags */
	uint			m_qflags;	/* quota status flags */
	uint			m_attroffset;	/* inode attribute offset */
	uint			m_dir_node_ents; /* #entries in a dir danode */
	uint			m_attr_node_ents; /* #entries in attr danode */
	int			m_ialloc_inos;	/* inodes in inode allocation */
	int			m_ialloc_blks;	/* blocks in inode allocation */
	int			m_litino;	/* size of inode union area */
	int			m_inoalign_mask;/* mask sb_inoalignmt if used */
	xfs_trans_reservations_t m_reservations;/* precomputed res values */
	__uint64_t		m_maxicount;	/* maximum inode count */
	int			m_dalign;	/* stripe unit */
	int			m_swidth;	/* stripe width */
	int			m_sinoalign;	/* stripe unit inode alignmnt */
	int			m_attr_magicpct;/* 37% of the blocksize */
	int			m_dir_magicpct;	/* 37% of the dir blocksize */
	__uint8_t		m_dirversion;	/* 1 or 2 */
	int			m_dirblksize;	/* directory block sz--bytes */
	int			m_dirblkfsbs;	/* directory block sz--fsbs */
	xfs_dablk_t		m_dirdatablk;	/* blockno of dir data v2 */
	xfs_dablk_t		m_dirleafblk;	/* blockno of dir non-data v2 */
	xfs_dablk_t		m_dirfreeblk;	/* blockno of dirfreeindex v2 */
} xfs_mount_t;
#define	XFS_DIR_IS_V1(mp)	((mp)->m_dirversion == 1)
#define	XFS_DIR_IS_V2(mp)	((mp)->m_dirversion == 2)

#define LIBXFS_MOUNT_ROOTINOS		0x0001
#define LIBXFS_MOUNT_DEBUGGER		0x0002
#define LIBXFS_MOUNT_32BITINODES	0x0004
#define LIBXFS_MOUNT_32BITINOOPT	0x0008
#define LIBXFS_MOUNT_COMPAT_ATTR	0x0010

#define LIBXFS_IHASHSIZE(sbp)		(1<<10)
#define LIBXFS_BHASHSIZE(sbp) 		(1<<10)

extern xfs_mount_t	*libxfs_mount (xfs_mount_t *, xfs_sb_t *,
				dev_t, dev_t, dev_t, int);
extern void	libxfs_mount_common (xfs_mount_t *, xfs_sb_t *);
extern xfs_agnumber_t	libxfs_initialize_perag (xfs_mount_t *, xfs_agnumber_t);
extern int	libxfs_initialize_perag_data (xfs_mount_t *, xfs_agnumber_t);
extern void	libxfs_umount (xfs_mount_t *);
extern int	libxfs_rtmount_init (xfs_mount_t *);
extern void	libxfs_rtmount_destroy (xfs_mount_t *);
extern void	libxfs_alloc_compute_maxlevels (xfs_mount_t *);
extern void	libxfs_bmap_compute_maxlevels (xfs_mount_t *, int);
extern void	libxfs_ialloc_compute_maxlevels (xfs_mount_t *);
extern void	libxfs_trans_init (xfs_mount_t *);


/*
 * Simple I/O interface
 */
typedef struct xfs_buf {
	struct cache_node	b_node;
	unsigned int		b_flags;
	xfs_daddr_t		b_blkno;
	unsigned		b_bcount;
	dev_t			b_dev;
	pthread_mutex_t		b_lock;
	void			*b_fsprivate;
	void			*b_fsprivate2;
	void			*b_fsprivate3;
	char			*b_addr;
#ifdef XFS_BUF_TRACING
	struct list_head	b_lock_list;
	const char		*b_func;
	const char		*b_file;
	int			b_line;
#endif
} xfs_buf_t;

enum xfs_buf_flags_t {	/* b_flags bits */
	LIBXFS_B_EXIT		= 0x0001,	/* ==LIBXFS_EXIT_ON_FAILURE */
	LIBXFS_B_DIRTY		= 0x0002,	/* buffer has been modified */
	LIBXFS_B_STALE		= 0x0004,	/* buffer marked as invalid */
	LIBXFS_B_UPTODATE	= 0x0008	/* buffer is sync'd to disk */
};

#define XFS_BUF_PTR(bp)			((bp)->b_addr)
#define xfs_buf_offset(bp, offset)	(XFS_BUF_PTR(bp) + (offset))
#define XFS_BUF_ADDR(bp)		((bp)->b_blkno)
#define XFS_BUF_SIZE(bp)		((bp)->b_bcount)
#define XFS_BUF_COUNT(bp)		((bp)->b_bcount)
#define XFS_BUF_TARGET(bp)		((bp)->b_dev)
#define XFS_BUF_SET_PTR(bp,p,cnt)	((bp)->b_addr = (char *)(p)); \
						XFS_BUF_SET_COUNT(bp,cnt)
#define XFS_BUF_SET_ADDR(bp,blk)	((bp)->b_blkno = (blk))
#define XFS_BUF_SET_COUNT(bp,cnt)	((bp)->b_bcount = (cnt))

#define XFS_BUF_FSPRIVATE(bp,type)	((type)(bp)->b_fsprivate)
#define XFS_BUF_SET_FSPRIVATE(bp,val)	(bp)->b_fsprivate = (void *)(val)
#define XFS_BUF_FSPRIVATE2(bp,type)	((type)(bp)->b_fsprivate2)
#define XFS_BUF_SET_FSPRIVATE2(bp,val)	(bp)->b_fsprivate2 = (void *)(val)
#define XFS_BUF_FSPRIVATE3(bp,type)	((type)(bp)->b_fsprivate3)
#define XFS_BUF_SET_FSPRIVATE3(bp,val)	(bp)->b_fsprivate3 = (void *)(val)

#define XFS_BUF_SET_PRIORITY(bp,pri)	cache_node_set_priority( \
						libxfs_bcache, \
						(struct cache_node *)(bp), \
						(pri))
#define XFS_BUF_PRIORITY(bp)		(cache_node_get_priority( \
						(struct cache_node *)(bp)))

/* Buffer Cache Interfaces */

extern struct cache	*libxfs_bcache;
extern struct cache_operations	libxfs_bcache_operations;

#ifdef XFS_BUF_TRACING

#define libxfs_readbuf(dev, daddr, len, flags) \
		libxfs_trace_readbuf(__FUNCTION__, __FILE__, __LINE__, (dev), (daddr), (len), (flags))
#define libxfs_writebuf(buf, flags) \
		libxfs_trace_writebuf(__FUNCTION__, __FILE__, __LINE__, (buf), (flags))
#define libxfs_getbuf(dev, daddr, len) \
		libxfs_trace_getbuf(__FUNCTION__, __FILE__, __LINE__, (dev), (daddr), (len))
#define libxfs_putbuf(buf) \
		libxfs_trace_putbuf(__FUNCTION__, __FILE__, __LINE__, (buf))

extern xfs_buf_t *libxfs_trace_readbuf(const char *, const char *, int, dev_t, xfs_daddr_t, int, int);
extern int	libxfs_trace_writebuf(const char *, const char *, int, xfs_buf_t *, int);
extern xfs_buf_t *libxfs_trace_getbuf(const char *, const char *, int, dev_t, xfs_daddr_t, int);
extern void	libxfs_trace_putbuf (const char *, const char *, int, xfs_buf_t *);

#else

extern xfs_buf_t *libxfs_readbuf(dev_t, xfs_daddr_t, int, int);
extern int	libxfs_writebuf(xfs_buf_t *, int);
extern xfs_buf_t *libxfs_getbuf(dev_t, xfs_daddr_t, int);
extern void	libxfs_putbuf (xfs_buf_t *);

#endif

extern xfs_buf_t *libxfs_getsb(xfs_mount_t *, int);
extern void	libxfs_bcache_purge(void);
extern void	libxfs_bcache_flush(void);
extern void	libxfs_purgebuf(xfs_buf_t *);
extern int	libxfs_bcache_overflowed(void);
extern int	libxfs_bcache_usage(void);

/* Buffer (Raw) Interfaces */
extern xfs_buf_t *libxfs_getbufr(dev_t, xfs_daddr_t, int);
extern void	libxfs_putbufr(xfs_buf_t *);

extern int	libxfs_writebuf_int(xfs_buf_t *, int);
extern int	libxfs_readbufr(dev_t, xfs_daddr_t, xfs_buf_t *, int, int);

extern int libxfs_bhash_size;
extern int libxfs_ihash_size;

#define LIBXFS_BREAD	0x1
#define LIBXFS_BWRITE	0x2
#define LIBXFS_BZERO	0x4

extern void	libxfs_iomove (xfs_buf_t *, uint, int, void *, int);


/*
 * Transaction interface
 */

typedef struct xfs_log_item {
	struct xfs_log_item_desc	*li_desc;	/* ptr to current desc*/
	struct xfs_mount		*li_mountp;	/* ptr to fs mount */
	uint				li_type;	/* item type */
} xfs_log_item_t;

typedef struct xfs_inode_log_item {
	xfs_log_item_t		ili_item;		/* common portion */
	struct xfs_inode	*ili_inode;		/* inode pointer */
	unsigned short		ili_flags;		/* misc flags */
	unsigned int		ili_last_fields;	/* fields when flushed*/
	xfs_inode_log_format_t	ili_format;		/* logged structure */
} xfs_inode_log_item_t;

typedef struct xfs_buf_log_item {
	xfs_log_item_t		bli_item;	/* common item structure */
	struct xfs_buf		*bli_buf;	/* real buffer pointer */
	unsigned int		bli_flags;	/* misc flags */
	unsigned int		bli_recur;	/* recursion count */
	xfs_buf_log_format_t	bli_format;	/* in-log header */
} xfs_buf_log_item_t;

#include <xfs/xfs_trans.h>

typedef struct xfs_trans {
	unsigned int	t_type;			/* transaction type */
	unsigned int	t_log_res;		/* amt of log space resvd */
	unsigned int	t_log_count;		/* count for perm log res */
	xfs_mount_t	*t_mountp;		/* ptr to fs mount struct */
	unsigned int	t_flags;		/* misc flags */
	long		t_icount_delta;		/* superblock icount change */
	long		t_ifree_delta;		/* superblock ifree change */
	long		t_fdblocks_delta;	/* superblock fdblocks chg */
	long		t_frextents_delta;	/* superblock freextents chg */
	unsigned int	t_items_free;		/* log item descs free */
	xfs_log_item_chunk_t	t_items;	/* first log item desc chunk */
} xfs_trans_t;

extern xfs_trans_t	*libxfs_trans_alloc (xfs_mount_t *, int);
extern xfs_trans_t	*libxfs_trans_dup (xfs_trans_t *);
extern int	libxfs_trans_reserve (xfs_trans_t *, uint,uint,uint,uint,uint);
extern int	libxfs_trans_commit (xfs_trans_t *, uint, xfs_lsn_t *);
extern void	libxfs_trans_cancel (xfs_trans_t *, int);
extern void	libxfs_mod_sb (xfs_trans_t *, __int64_t);
extern xfs_buf_t	*libxfs_trans_getsb (xfs_trans_t *, xfs_mount_t *, int);

extern int	libxfs_trans_iget (xfs_mount_t *, xfs_trans_t *, xfs_ino_t,
				uint, uint, struct xfs_inode **);
extern void	libxfs_trans_iput(xfs_trans_t *, struct xfs_inode *, uint);
extern void	libxfs_trans_ijoin (xfs_trans_t *, struct xfs_inode *, uint);
extern void	libxfs_trans_ihold (xfs_trans_t *, struct xfs_inode *);
extern void	libxfs_trans_log_inode (xfs_trans_t *, struct xfs_inode *,
				uint);

extern void	libxfs_trans_brelse (xfs_trans_t *, struct xfs_buf *);
extern void	libxfs_trans_binval (xfs_trans_t *, struct xfs_buf *);
extern void	libxfs_trans_bjoin (xfs_trans_t *, struct xfs_buf *);
extern void	libxfs_trans_bhold (xfs_trans_t *, struct xfs_buf *);
extern void	libxfs_trans_log_buf (xfs_trans_t *, struct xfs_buf *,
				uint, uint);
extern xfs_buf_t	*libxfs_trans_get_buf (xfs_trans_t *, dev_t,
				xfs_daddr_t, int, uint);
extern int	libxfs_trans_read_buf (xfs_mount_t *, xfs_trans_t *, dev_t,
				xfs_daddr_t, int, uint, struct xfs_buf **);


/*
 * Simple memory interface
 */
typedef struct xfs_zone {
	int	zone_unitsize;	/* Size in bytes of zone unit           */
	char	*zone_name;	/* tag name                             */
	int	allocated;	/* debug: How many currently allocated  */
} xfs_zone_t;

extern xfs_zone_t	*libxfs_zone_init (int, char *);
extern void	*libxfs_zone_zalloc (xfs_zone_t *);
extern void	libxfs_zone_free (xfs_zone_t *, void *);
extern void	*libxfs_malloc (size_t);
extern void	libxfs_free (void *);
extern void	*libxfs_realloc (void *, size_t);


/*
 * Inode interface
 */
typedef struct xfs_inode {
	struct cache_node	i_node;
	xfs_mount_t		*i_mount;	/* fs mount struct ptr */
	xfs_ino_t		i_ino;		/* inode number (agno/agino) */
	xfs_daddr_t		i_blkno;	/* blkno of inode buffer */
	dev_t			i_dev;		/* dev for this inode */
	ushort			i_len;		/* len of inode buffer */
	ushort			i_boffset;	/* off of inode in buffer */
	xfs_ifork_t		*i_afp;		/* attribute fork pointer */
	xfs_ifork_t		i_df;		/* data fork */
	xfs_trans_t		*i_transp;	/* ptr to owning transaction */
	xfs_inode_log_item_t	*i_itemp;	/* logging information */
	unsigned int		i_delayed_blks;	/* count of delay alloc blks */
	xfs_dinode_core_t	i_d;		/* most of ondisk inode */
} xfs_inode_t;

#define LIBXFS_ATTR_ROOT	0x0002	/* use attrs in root namespace */
#define LIBXFS_ATTR_SECURE	0x0008	/* use attrs in security namespace */
#define LIBXFS_ATTR_CREATE	0x0010	/* create, but fail if attr exists */
#define LIBXFS_ATTR_REPLACE	0x0020	/* set, but fail if attr not exists */

typedef struct cred {
	uid_t	cr_uid;
	gid_t	cr_gid;
} cred_t;

extern int	libxfs_inode_alloc (xfs_trans_t **, xfs_inode_t *, mode_t,
				nlink_t, xfs_dev_t, struct cred *,
				struct fsxattr *, xfs_inode_t **);
extern void	libxfs_trans_inode_alloc_buf (xfs_trans_t *, xfs_buf_t *);

extern void	libxfs_idata_realloc (xfs_inode_t *, int, int);
extern void	libxfs_idestroy_fork (xfs_inode_t *, int);
extern int	libxfs_iformat (xfs_inode_t *, xfs_dinode_t *);
extern void	libxfs_ichgtime (xfs_inode_t *, int);
extern int	libxfs_iflush_int (xfs_inode_t *, xfs_buf_t *);
extern int	libxfs_itobp (xfs_mount_t *, xfs_trans_t *, xfs_inode_t *,
				xfs_dinode_t **, xfs_buf_t **, xfs_daddr_t);
extern int	libxfs_iread (xfs_mount_t *, xfs_trans_t *, xfs_ino_t,
				xfs_inode_t *, xfs_daddr_t);

/* Inode Cache Interfaces */
extern struct cache	*libxfs_icache;
extern struct cache_operations	libxfs_icache_operations;
extern void	libxfs_icache_purge (void);
extern int	libxfs_iget (xfs_mount_t *, xfs_trans_t *, xfs_ino_t,
				uint, xfs_inode_t **, xfs_daddr_t);
extern void	libxfs_iput (xfs_inode_t *, uint);


/*
 * Directory interface
 */
#include <xfs/xfs_dir_leaf.h>
#include <xfs/xfs_dir2_data.h>
#include <xfs/xfs_dir2_leaf.h>
#include <xfs/xfs_dir2_block.h>
#include <xfs/xfs_dir2_node.h>

extern void	libxfs_dir_mount (xfs_mount_t *);
extern void	libxfs_dir2_mount (xfs_mount_t *);
extern int	libxfs_dir_init (xfs_trans_t *, xfs_inode_t *, xfs_inode_t *);
extern int	libxfs_dir2_init (xfs_trans_t *, xfs_inode_t *, xfs_inode_t *);
extern int	libxfs_dir_createname (xfs_trans_t *, xfs_inode_t *, uchar_t *,
				int, xfs_ino_t, xfs_fsblock_t *,
				xfs_bmap_free_t *, xfs_extlen_t);
extern int	libxfs_dir2_createname (xfs_trans_t *, xfs_inode_t *, uchar_t *,
				int, xfs_ino_t, xfs_fsblock_t *,
				xfs_bmap_free_t *, xfs_extlen_t);
extern int	libxfs_dir_lookup (xfs_trans_t *, xfs_inode_t *,
				uchar_t *, int, xfs_ino_t *);
extern int	libxfs_dir2_lookup (xfs_trans_t *, xfs_inode_t *,
				uchar_t *, int, xfs_ino_t *);
extern int	libxfs_dir_replace (xfs_trans_t *, xfs_inode_t *,
				uchar_t *, int, xfs_ino_t, xfs_fsblock_t *,
				xfs_bmap_free_t *, xfs_extlen_t);
extern int	libxfs_dir2_replace (xfs_trans_t *, xfs_inode_t *,
				uchar_t *, int, xfs_ino_t, xfs_fsblock_t *,
				xfs_bmap_free_t *, xfs_extlen_t);
extern int	libxfs_dir_removename (xfs_trans_t *, xfs_inode_t *,
				uchar_t *, int, xfs_ino_t, xfs_fsblock_t *,
				xfs_bmap_free_t *, xfs_extlen_t);
extern int	libxfs_dir2_removename (xfs_trans_t *, xfs_inode_t *,
				uchar_t *, int, xfs_ino_t, xfs_fsblock_t *,
				xfs_bmap_free_t *, xfs_extlen_t);
extern int	libxfs_dir_bogus_removename (xfs_trans_t *, xfs_inode_t *,
				uchar_t *, xfs_fsblock_t *, xfs_bmap_free_t *,
				xfs_extlen_t, xfs_dahash_t, int);
extern int	libxfs_dir2_bogus_removename (xfs_trans_t *, xfs_inode_t *,
				uchar_t *, xfs_fsblock_t *, xfs_bmap_free_t *,
				xfs_extlen_t, xfs_dahash_t, int);


/*
 * Block map interface
 */
extern int	libxfs_bmapi (xfs_trans_t *, xfs_inode_t *, xfs_fileoff_t,
				xfs_filblks_t, int, xfs_fsblock_t *,
				xfs_extlen_t, xfs_bmbt_irec_t *, int *,
				xfs_bmap_free_t *);
extern int	libxfs_bmapi_single(xfs_trans_t *, xfs_inode_t *, int,
				xfs_fsblock_t *, xfs_fileoff_t);
extern int	libxfs_bmap_finish (xfs_trans_t **, xfs_bmap_free_t *,
				xfs_fsblock_t, int *);
extern void	libxfs_bmap_cancel(xfs_bmap_free_t *);
extern int	libxfs_bmap_next_offset (xfs_trans_t *, xfs_inode_t *,
				xfs_fileoff_t *, int);
extern int	libxfs_bmap_last_offset(xfs_trans_t *, xfs_inode_t *,
				xfs_fileoff_t *, int);
extern int	libxfs_bunmapi (xfs_trans_t *, xfs_inode_t *, xfs_fileoff_t,
				xfs_filblks_t, int, xfs_extnum_t,
				xfs_fsblock_t *, xfs_bmap_free_t *, int *);
extern void	libxfs_bmap_del_free (xfs_bmap_free_t *,
				xfs_bmap_free_item_t *, xfs_bmap_free_item_t *);


/*
 * All other routines we want to keep common...
 */

extern int	libxfs_highbit32 (__uint32_t);
extern int	libxfs_highbit64 (__uint64_t);
extern uint	libxfs_da_log2_roundup (uint);

extern void	libxfs_xlate_sb (void *, xfs_sb_t *, int, __int64_t);
extern void	libxfs_xlate_dinode_core (xfs_caddr_t buf,
				xfs_dinode_core_t *, int);

extern int	libxfs_alloc_fix_freelist (xfs_alloc_arg_t *, int);
extern int	libxfs_alloc_file_space (xfs_inode_t *, xfs_off_t,
				xfs_off_t, int, int);

extern xfs_dahash_t	libxfs_da_hashname (const uchar_t *, int);
extern int	libxfs_attr_leaf_newentsize (int, int, int, int *);
extern int	libxfs_attr_set_int (xfs_inode_t*, const char *, int, char *,
				int, int);
extern int	libxfs_attr_remove_int (xfs_inode_t *, const char *, int, int);


extern void	libxfs_bmbt_get_all (xfs_bmbt_rec_t *, xfs_bmbt_irec_t *);
#if __BYTE_ORDER != __BIG_ENDIAN
extern void	libxfs_bmbt_disk_get_all (xfs_bmbt_rec_t *, xfs_bmbt_irec_t *);
#else
# define libxfs_bmbt_disk_get_all(r,s)	libxfs_bmbt_get_all(r,s)
#endif

extern int	libxfs_free_extent (xfs_trans_t *, xfs_fsblock_t, xfs_extlen_t);
extern int	libxfs_rtfree_extent (xfs_trans_t *, xfs_rtblock_t,
				xfs_extlen_t);

/* Directory/Attribute routines used by xfs_repair */
extern void	libxfs_da_bjoin (xfs_trans_t *, xfs_dabuf_t *);
extern int	libxfs_da_shrink_inode (xfs_da_args_t *, xfs_dablk_t,
				xfs_dabuf_t *);
extern int	libxfs_da_grow_inode (xfs_da_args_t *, xfs_dablk_t *);
extern void	libxfs_da_bhold (xfs_trans_t *, xfs_dabuf_t *);
extern void	libxfs_da_brelse (xfs_trans_t *, xfs_dabuf_t *);
extern int	libxfs_da_read_bufr (xfs_trans_t *, xfs_inode_t *, xfs_dablk_t,
				xfs_daddr_t, xfs_dabuf_t **, int);
extern int	libxfs_da_read_buf (xfs_trans_t *, xfs_inode_t *,
				xfs_dablk_t, xfs_daddr_t, xfs_dabuf_t **, int);
extern int	libxfs_da_get_buf (xfs_trans_t *, xfs_inode_t *,
				xfs_dablk_t, xfs_daddr_t, xfs_dabuf_t **, int);
extern void	libxfs_da_log_buf (xfs_trans_t *, xfs_dabuf_t *, uint, uint);
extern int	libxfs_dir2_shrink_inode (xfs_da_args_t *, xfs_dir2_db_t,
				xfs_dabuf_t *);
extern int	libxfs_dir2_grow_inode (xfs_da_args_t *, int, xfs_dir2_db_t *);
extern int	libxfs_dir2_isleaf (xfs_trans_t *, xfs_inode_t *, int *);
extern int	libxfs_dir2_isblock (xfs_trans_t *, xfs_inode_t *, int *);
extern void	libxfs_dir2_data_use_free (xfs_trans_t *, xfs_dabuf_t *,
				xfs_dir2_data_unused_t *, xfs_dir2_data_aoff_t,
				xfs_dir2_data_aoff_t, int *, int *);
extern void	libxfs_dir2_data_make_free (xfs_trans_t *, xfs_dabuf_t *,
				xfs_dir2_data_aoff_t, xfs_dir2_data_aoff_t,
				int *, int *);
extern void	libxfs_dir2_data_log_entry (xfs_trans_t *, xfs_dabuf_t *,
				xfs_dir2_data_entry_t *);
extern void	libxfs_dir2_data_log_header (xfs_trans_t *, xfs_dabuf_t *);
extern void	libxfs_dir2_data_freescan (xfs_mount_t *, xfs_dir2_data_t *,
				int *, char *);
extern void	libxfs_dir2_free_log_bests (xfs_trans_t *, xfs_dabuf_t *,
				int, int);

/* Shared utility routines */
extern unsigned int	libxfs_log2_roundup(unsigned int i);

extern void cmn_err(int, char *, ...);
enum ce { CE_DEBUG, CE_CONT, CE_NOTE, CE_WARN, CE_ALERT, CE_PANIC };


#define LIBXFS_BBTOOFF64(bbs)	(((xfs_off_t)(bbs)) << BBSHIFT)
extern int		libxfs_nproc(void);
extern unsigned long	libxfs_physmem(void);	/* in kilobytes */

#include <xfs/xfs_ialloc.h>
#include <xfs/xfs_rtalloc.h>

#include <xfs/xfs_attr_leaf.h>
#include <xfs/xfs_quota.h>
#include <xfs/xfs_trans_space.h>
#include <xfs/xfs_imap.h>
#include <xfs/xfs_log.h>
#include <xfs/xfs_log_priv.h>

#endif	/* __LIBXFS_H__ */
