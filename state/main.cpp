#pragma comment(linker,"/STACK:64000000")
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

int move_by_chr[255];
vector<string> powerphrases;
bool quiet = false;


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
				DFOR(b,a-1,0)
					FOR(c,0,width-1)
						board[b+1][c] = board[b][c];
		}
	}

	int get_value()
	{
		int re = 0;
		FOR(a,0,height-1) FOR(b,0,width-1)
			if (board[a][b])
				re += a*3+1;
		FA(a,unit) re += unit[a].Y*3+1;
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
		out.tag = "bla";
		out.solution = "";

		FOR(a,0,inp.sourceLength-1)
		{
			int ind = (rnd.next()) % SZ(inp.units);
			PAR pivot;
			vector< PAR > unit;
			unit_to_unit( inp.units[ind], pivot, unit );
			if (!S.spawn_unit( pivot, unit )) break;
			S.render();
			calc_all_end_positions( S );
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
			ass( S.get_value() == best_value );
			S.lock_unit();
			S.render();

			out.solution += cmds[best];
		}
		answer.push_back( out );
	}
	return answer;

	/*S.init( 10, 10 );
	S.board[9][1] = true;
	S.board[8][6] = true;
	S.board[9][6] = true;

	PAR pi = make_pair( 0, 0 );
	vector< PAR > un;
	//un.push_back( make_pair( 0, 0 ) );
	un.push_back( make_pair( 0, 1 ) );
	un.push_back( make_pair( 1, 1 ) );
	un.push_back( make_pair( 2, 2 ) );
	un.push_back( make_pair( 3, 2 ) );
	S.spawn_unit( pi, un );

	S.render();

	calc_all_end_positions( S );

	cout << SZ(end_pos) << "\n";
	FA(a,end_pos)
	{
		cout << end_pos[a].first.X << " " << end_pos[a].first.Y << " " << end_pos[a].second << " ";
		cout << cmds[a] << "\n";
	}*/
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
	sprintf( path, "../solutions/solution_%d_rip_2.json", problem );
	FILE * file_out = fopen( path, "w" );
	fprintf( file_out, "%s", res.c_str() );
	fclose( file_out );
}

int main(int argc, char** argv)
{
	System::ParseArgs(argc, argv);
	powerphrases = System::GetArgValues("p");
	vector<string> files = System::GetArgValues("f");

	string symb =
		"p'!.03"
		"aghij4"
		"lmno 5"
		"bcefy2"
		"dqrvz1"
		"kstuwx";
	FA(a,symb) move_by_chr[symb[a]] = a/6;

	if (files.empty())
	{

		freopen("input.txt","r",stdin);
		freopen("output.txt","w",stdout);

		//serializeJson( TMP() );

		FOR(a,0,23) sol( a );

	} else {

		quiet = true;
		vector<OUTPUT> res, tmp;
		//printf("%d\n", (int)files.size());
		for (int i = 0; i < files.size(); i++)
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
