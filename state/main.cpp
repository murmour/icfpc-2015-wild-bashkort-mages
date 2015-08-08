#pragma comment(linker,"/STACK:256000000")
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <cmath>
#include <map>
#include <set>
#include <ctime>
#include <algorithm>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include "common.h"
#include "system.h"

using namespace std;
using namespace PlatBox;

#define WR printf
#define RE scanf
#define PB push_back
#define Y second
#define X first

#define FOR(i,k,n) for(int i=(k); i<=(n); i++)
#define DFOR(i,k,n) for(int i=(k); i>=(n); i--)
#define SZ(a) (int)((a).size())
#define FA(i,v) FOR(i,0,SZ(v)-1)
#define RFA(i,v) DFOR(i,SZ(v)-1,0)
#define CLR(a) memset(a, 0, sizeof(a))

#define LL long long
#define VI  vector<int>
#define PAR pair<int ,int>
#define o_O 1000000000

void __never(int a){printf("\nOPS %d", a);}
#define ass(s) {if (!(s)) {__never(__LINE__);cout.flush();cerr.flush();abort();}}

#define NN 100

string guten_tag = "aperture_1";
int move_by_chr[255];
vector<string> powerphrases;
bool quiet = false;

/*string symbols =
	"p'!.03"
	"aghij4"
	"lmno 5"
	"bcefy2"
	"dqrvz1"
	"kstuwx";*/

typedef unsigned int uint;
const int MAX_VERS = 2000;
int n_vers = 0;
map<vector<int>, int> vers;
const char letters[] = "p'!.03aghij4lmno 5bcefy2dqrvz1kstuwx";
const int n_letters = sizeof(letters);

int a_next[MAX_VERS][n_letters];
int a_mask[MAX_VERS][n_letters];

int get_ver(const vector<int> lens, bool &added)
{
	added = false;
	if (vers.find(lens) != vers.end()) return vers[lens];
	ass(n_vers < MAX_VERS);
	vers[lens] = n_vers;
	added = true;
	n_vers++;
	return vers[lens];
}

void automata_dfs(int prev, string s0)
{
	int n_words = powerphrases.size();
	for (uint i = 0; i < n_letters; i++)
	{
		string s = s0 + letters[i];
		int mask = 0;
		// compute vector
		vector<int> lens(n_words);
		for (uint j = 0; j < powerphrases.size(); j++)
		{
			int plen = powerphrases[j].size();

			int maxp = 0;
			for (int le = 1; le <= (int)s.size() && le <= plen; le++)
			{
				if (powerphrases[j].substr(0, le) == s.substr(s.size()-le, le))
				{
					if (le < plen) lens[j] = le;
					maxp = le;
				}
			}
			if (maxp == plen) mask |= (1 << j);
		}
		bool added = false;
		int v = get_ver(lens, added);
		a_next[prev][i] = v;
		a_mask[prev][i] = mask;
		if (added) automata_dfs(v, s);
	}
}

void build_automata()
{
	ass( powerphrases.size() <= 31 );
	n_vers = 0;
	vers.clear();
	bool dummy;
	int v = get_ver(vector<int>(powerphrases.size()), dummy);
	automata_dfs(v, "");
}

void print_automata()
{
	printf("n_vers = %d\n", n_vers);
	for (int i = 0; i < n_vers; i++)
	{
		for (int j = 0; j < n_letters; j++)
			if (a_next[i][j] || a_mask[i][j])
				printf("%d -%c-> %d (%d)\n", i, letters[j], a_next[i][j], a_mask[i][j]);
	}
}

struct STATE
{
	bool board[NN][NN];
	int height, width;

	PAR pivot;
	vector< PAR > unit;
	int rotate;

	int max_rotate;

	void init( int w, int h )
	{
		CLR( board );
		height = h;
		width = w;
	}

	void move_pnt( PAR & p, int dir, int d )
	{
		if (d<0)
		{
			d *= -1;
			dir += 3;
			if (dir>=6) dir -= 6;
		}
		if ((p.Y & 1)==0)
		{
			if (dir==0) { p.X -= d; }
			else if (dir==1) { p.X -= ((d+1)>>1); p.Y += d; }
			else if (dir==2) { p.X += (d>>1); p.Y += d; }
			else if (dir==3) { p.X += d; }
			else if (dir==4) { p.X += (d>>1); p.Y -= d; }
			else if (dir==5) { p.X -= ((d+1)>>1); p.Y -= d; }
		}
		else
		{
			if (dir==0) { p.X -= d; }
			else if (dir==1) { p.X -= (d>>1); p.Y += d; }
			else if (dir==2) { p.X += ((d+1)>>1); p.Y += d; }
			else if (dir==3) { p.X += d; }
			else if (dir==4) { p.X += ((d+1)>>1); p.Y -= d; }
			else if (dir==5) { p.X -= (d>>1); p.Y -= d; }
		}
	}

	// cmd:
	// 0 - left
	// 1 - left-down
	// 2 - right-down
	// 3 - right
	// 4 - rotate cw
	// 5 - rotate ccw

	bool can_move( int move )
	{
		FA(a,unit)
		{
			PAR p = unit[a];
			if (move <= 3)
			{
				move_pnt( p, move, 1 );
			}
			else
			{
				PAR p_end = pivot;
				PAR p1 = pivot;
				move_pnt( p1, 5, pivot.Y-p.Y );
				move_pnt( p_end, (move==4 ? 4 : 0), pivot.Y-p.Y );
				move_pnt( p_end, (move==4 ? 5 : 1), p1.X-p.X );
                p = p_end;
			}
			if (!(0<=p.X && p.X<width && 0<=p.Y && p.Y<height)) return false;
			if (board[p.Y][p.X]) return false;
		}
		return true;
	}

	void do_move( int move )
	{
		for( int a=0; a<=(int)unit.size(); a++)
		{
			PAR p = pivot;
			if (a<(int)unit.size()) p = unit[a];
			if (move <= 3)
			{
				move_pnt( p, move, 1 );
			}
			else
			{
				PAR p_end = pivot;
				PAR p1 = pivot;
				move_pnt( p1, 5, pivot.Y-p.Y );
				//cerr << pivot.Y-p.Y << " " << p1.X-p.X << "\n";
				move_pnt( p_end, (move==4 ? 4 : 0), pivot.Y-p.Y );
				move_pnt( p_end, (move==4 ? 5 : 1), p1.X-p.X );
				p = p_end;
			}
			if (a<(int)unit.size()) unit[a] = p;
			else pivot = p;
		}
		if (move==4)
		{
			rotate++;
			if (rotate==max_rotate) rotate = 0;
		}
		if (move==5)
		{
			rotate--;
			if (rotate<0) rotate = max_rotate-1;
		}
	}

	void undo_move( int move )
	{
		if (move <= 3)
		{
			int m2 = move+3;
			if (m2>=6) m2-=6;
			for( int a=0; a<(int)unit.size(); a++)
				move_pnt( unit[a], m2, 1 );
			move_pnt( pivot, m2, 1 );
		}
		else do_move( move==4 ? 5 : 4 );
	}

	void do_commands( string cmds )
	{
		FA(a,cmds)
		{
			int move = move_by_chr[cmds[a]];
			if (can_move(move))
				do_move(move);
		}
	}

	void lock_unit()
	{
		FA(a,unit)
		{
			ass( !board[unit[a].Y][unit[a].X] );
			board[unit[a].Y][unit[a].X] = true;
		}
		DFOR(a,height-1,0)
		{
			bool flag = true;
			FOR(b,0,width-1)
				if (!board[a][b])
					flag = false;
			if (flag)
			{
				DFOR(b,a-1,0)
					FOR(c,0,width-1)
						board[b+1][c] = board[b][c];
				FOR(c,0,width-1)
					board[0][c] = false;
				a++;
			}
		}
	}

	int get_value()
	{
		int re = 0;
		FOR(a,0,height-1) FOR(b,0,width-1)
			if (board[a][b])
				re += a*3+1;
		FA(a,unit) re += unit[a].Y*3+1;
		int lines = 0;
		FOR(a,0,height-1)
		{
			bool flag = true;
			FOR(b,0,width-1)
				if (!board[a][b])
				{
					bool flag2 = false;
					FA(c,unit)
						if (unit[c] == make_pair( b, a ))
							flag2 = true;
					if (!flag2) flag = false;
				}
			if (flag) lines++;
		}
		re += lines*lines*width*10;

		FOR(a,0,height-1)
			FOR(b,0,width-1)
				if (board[a][b])
					FOR(c,0,5)
					{
						PAR p = make_pair( b, a );
						move_pnt( p, c, 1 );
						bool flag = true;
						FA(d,unit)
							if (unit[d] == p)
								flag = false;
						if (flag)
							if (0<=p.X && p.X<width && 0<=p.Y && p.Y<height)
								if (!board[p.Y][p.X])
									re -= 2;
					}
		FA(a,unit) FOR(b,0,5)
		{
			PAR p = unit[a];
			move_pnt( p, b, 1 );
			bool flag = true;
			FA(c,unit)
				if (unit[c] == p)
					flag = false;
			if (flag)
				if (0<=p.X && p.X<width && 0<=p.Y && p.Y<height)
					if (!board[p.Y][p.X])
						re -= 2;
		}
				
		return re;
	}

	int calc_max_rotate()
	{
		sort( unit.begin(), unit.end() );
		vector< PAR > v = unit;
		FOR(a,0,5)
		{
			do_move( 4 );
			sort( unit.begin(), unit.end() );
			if (unit==v) return a+1;
		}
		ass( false );
		return -1;
	}

	bool spawn_unit( PAR n_pivot, vector< PAR > n_unit )
	{
		int mi = o_O, ma = -o_O;
		FA(a,n_unit) mi = min( mi, n_unit[a].Y );
		FA(a,n_unit) move_pnt( n_unit[a], 5, mi );
		move_pnt( n_pivot, 5, mi );

		mi = o_O;
		FA(a,n_unit)
		{
			mi = min( mi, n_unit[a].X );
			ma = max( ma, n_unit[a].X );
		}

		int d = (width - (ma-mi+1))/2 - mi;
		FA(a,n_unit) move_pnt( n_unit[a], 3, d );
		move_pnt( n_pivot, 3, d );

		FA(a,n_unit) if (board[n_unit[a].Y][n_unit[a].X]) return false;
		pivot = n_pivot;
		unit = n_unit;

		max_rotate = calc_max_rotate();
		//cerr << max_rotate << "\n";
		rotate = 0;
		return true;
	}

	void render()
	{
		if (quiet) return;
		FOR(a,0,height-1)
		{
			if (a&1) cout << " ";
			FOR(b,0,width-1)
			{
				bool flag = false;
				FA(c,unit) if (unit[c] == make_pair( b, a )) flag = true;
				if (pivot == make_pair( b, a )) cout << "* ";
				else if (flag) cout << "$ ";
				else if (board[a][b]) cout << "# ";
				else cout << ". ";
			}
			cout << "\n";
		}
		cout << "\n";
	}
};

struct CELL
{
	int x, y;
	FLD_BEGIN FLD(x) FLD(y) FLD_END
};


struct UNIT
{
	vector< CELL > members;
	CELL pivot;
	FLD_BEGIN FLD(members) FLD(pivot) FLD_END
};

struct INPUT
{
	int id;
	vector< UNIT > units;
	int width;
	int height;
	vector< CELL > filled;
	int sourceLength;
	vector< unsigned int > sourceSeeds;

	FLD_BEGIN FLD(id) FLD(units) FLD(width) FLD(height)
		FLD(filled) FLD(sourceLength) FLD(sourceSeeds) FLD_END
};

struct OUTPUT
{
	int problemId;
	unsigned int seed;
	string tag;
	string solution;
	
	FLD_BEGIN FLD(problemId) FLD(seed) FLD(tag) FLD(solution) FLD_END
};

struct DP_STATE
{
	PAR pivot;
	int rotate;
	PAR rot_range;
	int from; // 0 - ?, 1 - left, 2 - right
	int node;
};

struct DP_VALUE
{
	LL cost;
	int mx_len;
	int sum;
	int end_value;
	int nxt;
	DP_VALUE()
	{
		cost = 0;
		mx_len = 0;
		sum = 0;
		end_value = 0;
		nxt = -1;
	}
	void recalc_cost()
	{
		cost = (LL)end_value*100000 + mx_len*1000 + sum;
	}
};

bool operator< ( const DP_STATE & A, const DP_STATE & B )
{
	if (A.pivot != B.pivot) return A.pivot < B.pivot;
	if (A.rotate != B.rotate) return A.rotate < B.rotate;
	if (A.rot_range != B.rot_range) return A.rot_range < B.rot_range;
	if (A.from != B.from) return A.from < B.from;
	return A.node < B.node;
}

map< DP_STATE, DP_VALUE > Map;

DP_STATE do_dp_move( STATE & sta, DP_STATE dps, int move )
{
	DP_STATE dps2 = dps;

	dps2.pivot = sta.pivot;
	dps2.rotate = sta.rotate;
	if (move==0) dps2.from = 2;
	if (move==1 || move==2)
	{
		dps2.from = 0;
		dps2.rot_range = make_pair( dps2.rotate, dps2.rotate );
	}
	if (move==3) dps2.from = 1;
	if (move==4)
	{
		dps2.rot_range.second = dps2.rotate;
		dps2.from = 0;
	}
	if (move==5)
	{
		dps2.rot_range.first = dps2.rotate;
		dps2.from = 0;
	}

	return dps2;
}

set< DP_STATE > was;

DP_VALUE get_dp( STATE & sta, DP_STATE dps )
{
	if (Map.find(dps)!=Map.end()) return Map[dps];

	ass( was.find( dps )==was.end() );
	was.insert( dps );

	DP_VALUE v;
	FOR(move,0,5)
	{
		bool flag = true;
		if (move==0 && dps.from==1) flag = false;
		if (move==3 && dps.from==2) flag = false;
		if (move==4)
		{
			int r = dps.rotate+1;
			if (r==sta.max_rotate) r=0;
			if (r==dps.rot_range.first || r==dps.rot_range.second)
				flag = false;
			if (dps.rotate==dps.rot_range.first && dps.rot_range.first!=dps.rot_range.second)
				flag = false;
			if (sta.max_rotate==1)
				flag = false;
		}
		if (move==5)
		{
			int r = dps.rotate-1;
			if (r<0) r=sta.max_rotate-1;
			if (r==dps.rot_range.first || r==dps.rot_range.second)
				flag = false;
			if (dps.rotate==dps.rot_range.second && dps.rot_range.first!=dps.rot_range.second)
				flag = false;
			if (sta.max_rotate==1)
				flag = false;
		}

		if (flag && sta.can_move( move ))
		{
			sta.do_move( move );
			DP_STATE dps2 = do_dp_move( sta, dps, move );

			FOR(c,0,5)
			{
				dps2.node = a_next[dps.node][move*6+c];

				DP_VALUE tmp = get_dp( sta, dps2 );

				int msk = a_mask[dps.node][move*6+c];
				FA(d,powerphrases) if ((msk>>d)&1)
				{
					tmp.mx_len = max( tmp.mx_len, SZ(powerphrases[d]) );
					tmp.sum += SZ(powerphrases[d]);
				}
				tmp.nxt = move*6+c;
				tmp.recalc_cost();
				if (v.cost < tmp.cost)
					v = tmp;
			}
			sta.undo_move( move );
		}
	}
	FOR(move,0,5)
		if (!sta.can_move( move ))
			FOR(c,0,5)
			{
				DP_VALUE tmp;
				int msk = a_mask[dps.node][move*6+c];
				FA(d,powerphrases) if ((msk>>d)&1)
				{
					tmp.mx_len = max( tmp.mx_len, SZ(powerphrases[d]) );
					tmp.sum += SZ(powerphrases[d]);
				}
				tmp.end_value = sta.get_value();
				tmp.nxt = move*6+c;
				tmp.recalc_cost();
				if (v.cost < tmp.cost)
					v = tmp;
			}
	Map[dps] = v;
	was.erase( dps );
	return v;
}

void calc_crazy_dp( STATE & sta, int starting_node )
{
	Map.clear();

	DP_STATE dps;
	dps.pivot = sta.pivot;
	dps.rotate = sta.rotate;
	dps.rot_range = make_pair( sta.rotate, sta.rotate );
	dps.from = 0;
	dps.node = starting_node;

	get_dp( sta, dps );
}

set< pair< PAR, int > > Set;
vector< pair< PAR, int > > end_pos;
vector< int > values;
vector< string > cmds;
//string cmd = "lLRr12";
string cmd = "palbdk";
string seq;

void dfs( STATE & sta )
{
	Set.insert( make_pair( sta.pivot, sta.rotate ) );
	int end_cmd = -1;
	FOR(a,0,5)
		if (sta.can_move(a))
		{
			int tmp = sta.rotate;
			sta.do_move( a );
			seq.push_back( cmd[a] );
			if (Set.find( make_pair( sta.pivot, sta.rotate ) ) == Set.end())
				dfs( sta );
			seq.resize( SZ(seq)-1 );
			sta.undo_move( a );
			ass( tmp == sta.rotate );
		}
		else end_cmd = a;
	if (end_cmd>=0)
	{
		end_pos.push_back( make_pair( sta.pivot, sta.rotate ) );
		values.push_back( sta.get_value() );
		seq.push_back( cmd[end_cmd] );
		cmds.push_back( seq );
		seq.resize( SZ(seq)-1 );
	}
}

void calc_all_end_positions( STATE & sta )
{
	Set.clear();
	seq.clear();
	end_pos.clear();
	values.clear();
	cmds.clear();
	dfs( sta );
}

struct RANDOM
{
	unsigned int seed;
	void set_seed( unsigned int s )
	{
		seed = s;
	}
	unsigned int next()
	{
		unsigned int re = (seed>>16) & ((1<<15)-1);
		seed = seed*1103515245 + 12345;
		return re;
	}
} rnd;

void unit_to_unit( UNIT & u, PAR & pivot, vector< PAR > & unit )
{
	pivot = make_pair( u.pivot.x, u.pivot.y );
	FA(a,u.members) unit.push_back( make_pair( u.members[a].x, u.members[a].y ) );
}

vector<OUTPUT> sol_internal( const char *path )
{

	FILE * file_in = fopen( path, "r" );
	ass( file_in );
	char buf[100];
	string str;
	while ( fgets( buf, 96, file_in ) ) str += string( buf );
	fclose( file_in );
	//cerr << str << "\n";

	Json::Reader rdr;
	Json::Value data;
	if (!rdr.parse(str, data, false))
		ass( false );
	INPUT inp;
	if (!deserializeJson( inp, data ))
		ass( false );

	vector< OUTPUT > answer;
	FA(z,inp.sourceSeeds)
	{
		STATE S;
		S.init( inp.width, inp.height );
		FA(a,inp.filled) S.board[inp.filled[a].y][inp.filled[a].x] = true;

		rnd.set_seed( inp.sourceSeeds[z] );

		OUTPUT out;
		out.problemId = inp.id;
		out.seed = inp.sourceSeeds[z];
		out.tag = guten_tag;
		out.solution = "";

		FOR(a,0,inp.sourceLength-1)
		{
			int ind = (rnd.next()) % SZ(inp.units);
			PAR pivot;
			vector< PAR > unit;
			unit_to_unit( inp.units[ind], pivot, unit );
			if (!S.spawn_unit( pivot, unit )) break;
			S.render();
			/*calc_all_end_positions( S );
			int ends = SZ(end_pos);
			int best = -1, best_value = -1;
			FOR(b,0,ends-1)
				if (values[b] > best_value)
				{
					best = b;
					best_value = values[b];
				}
			ass( best>=0 );
			S.do_commands( cmds[best] );
			ass( S.get_value() == best_value );*/
			calc_crazy_dp( S, 0 );
			DP_STATE dps;
			dps.pivot = S.pivot;
			dps.rotate = S.rotate;
			dps.rot_range = make_pair( S.rotate, S.rotate );
			dps.from = 0;
			dps.node = 0;

			while(1)
			{
				int nxt = Map[dps].nxt;
				out.solution.push_back( letters[nxt] );
				int move = nxt/6;
				if (S.can_move( move ))
					S.do_move( move );
				else break;
				DP_STATE dps2 = do_dp_move( S, dps, nxt/6 );
				dps2.node = a_next[dps.node][nxt];
				dps = dps2;
			}

			S.lock_unit();
			S.render();

			//out.solution += cmds[best];
		}
		answer.push_back( out );
	}

	return answer;
}

void sol (int problem)
{
	cerr << "problem " << problem << "\n";
	char path[1000];
	sprintf( path, "../qualifier-problems/problem_%d.json", problem );
	vector<OUTPUT> answer = sol_internal(path);
	Json::FastWriter fw;
	Json::Value data;
	data = serializeJson( answer );
	string res = fw.write( data );
	sprintf( path, "../solutions/solution_%d_%s.json", problem, guten_tag.c_str() );
	FILE * file_out = fopen( path, "w" );
	fprintf( file_out, "%s", res.c_str() );
	fclose( file_out );
}

int main(int argc, char** argv)
{
	System::ParseArgs(argc, argv);
	powerphrases = System::GetArgValues("p");
	vector<string> files = System::GetArgValues("f");

	FOR(a,0,35) move_by_chr[letters[a]] = a/6;

	if (files.empty())
	{
		//powerphrases.push_back("abaed");
		//powerphrases.push_back("aed");
		powerphrases.push_back("ei!");
		powerphrases.push_back("ia! ia!");
		powerphrases.push_back("r'lyeh");
		powerphrases.push_back("yuggoth");

		build_automata();
		//print_automata();
		//return 0;

		freopen("input.txt","r",stdin);
		freopen("output.txt","w",stdout);

		//serializeJson( TMP() );

		quiet = true;
		//FOR(a,0,23) sol( a );
		sol( 0 );

		cerr << clock() << "\n";
	} else {

		build_automata();
		quiet = true;
		vector<OUTPUT> res, tmp;
		//printf("%d\n", (int)files.size());
		for (int i = 0; i < (int)files.size(); i++)
		{
			//printf("File: %s\n", files[i].c_str());
			tmp = sol_internal(files[i].c_str());
			res.insert(res.end(), tmp.begin(), tmp.end());
		}
		Json::FastWriter fw;
		Json::Value data;
		data = serializeJson( res );
		string sres = fw.write( data );
		printf("%s", sres.c_str());

	}

	return 0;
}
